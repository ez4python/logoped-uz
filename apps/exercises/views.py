from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, Prefetch
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, FormView, View
from django.utils import timezone

from apps.exercises.forms import SubmissionForm, FeedbackForm
from apps.exercises.models import Exercise, Assignment, Submission, Course, Category


class AllCoursesView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'dashboard/all_courses.html'
    context_object_name = 'courses'
    paginate_by = 9
    login_url = reverse_lazy('login')

    def get_queryset(self):
        queryset = super().get_queryset()

        # Apply search filter if provided
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Apply category filter if provided
        category = self.request.GET.get('category', '')
        if category and category.isdigit():
            queryset = queryset.filter(category_id=int(category))

        # Annotate with exercise count
        queryset = queryset.annotate(exercises_count=Count('exercises'))

        # Check if user is enrolled in each course
        user_assignments = Assignment.objects.filter(student=self.request.user)
        enrolled_course_ids = set()

        for assignment in user_assignments:
            enrolled_course_ids.add(assignment.exercise.course_id)

        # Add is_enrolled flag to each course
        for course in queryset:
            course.is_enrolled = course.id in enrolled_course_ids

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'all_courses'

        # Add categories for filter dropdown
        context['categories'] = Category.objects.all()

        # Add search query and selected category for form
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')

        return context


class EnrollCourseView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        # Get all exercises for this course
        exercises = course.exercises.all().order_by('order')

        if not exercises.exists():
            messages.error(request, 'В этом курсе пока нет упражнений.')
            return redirect('all_courses')

        # Check if already enrolled in any exercise of this course
        existing_assignments = Assignment.objects.filter(
            student=request.user,
            exercise__course=course
        )

        if existing_assignments.exists():
            messages.info(request, 'Вы уже записаны на этот курс.')
            return redirect('course_detail', course_id=course_id)

        # Find a therapist (for demo, just get the first therapist)
        # In a real app, you'd have a more sophisticated assignment algorithm
        from django.contrib.auth import get_user_model
        User = get_user_model()
        therapist = User.objects.filter(is_therapist=True).first()

        if not therapist:
            messages.error(request, 'Не удалось найти доступного логопеда. Пожалуйста, попробуйте позже.')
            return redirect('all_courses')

        # Create assignments for all exercises in the course
        for exercise in exercises:
            Assignment.objects.create(
                exercise=exercise,
                student=request.user,
                therapist=therapist
            )

        messages.success(request, f'Вы успешно записались на курс "{course.title}".')
        return redirect('course_detail', course_id=course_id)


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'dashboard/course_detail.html'
    context_object_name = 'course'
    pk_url_kwarg = 'course_id'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all exercises for this course
        exercises = self.object.exercises.all().order_by('order')

        # Get assignments for this user and course
        assignments = Assignment.objects.filter(
            student=self.request.user,
            exercise__course=self.object
        ).select_related('exercise')

        # Create a dictionary to map exercise IDs to assignments
        assignment_map = {a.exercise_id: a for a in assignments}

        # Prepare exercises with assignment status
        exercise_list = []
        is_previous_completed = True  # First exercise is always available

        for exercise in exercises:
            assignment = assignment_map.get(exercise.id)
            is_completed = assignment and assignment.is_completed
            is_available = is_previous_completed

            exercise_data = {
                'id': exercise.id,
                'title': exercise.title,
                'description': exercise.description,
                'type': exercise.get_type_display(),
                'is_completed': is_completed,
                'is_available': is_available,
                'assignment_id': assignment.id if assignment else None
            }

            exercise_list.append(exercise_data)
            is_previous_completed = is_completed

        context['exercises'] = exercise_list

        # Calculate progress
        total_exercises = len(exercise_list)
        completed_exercises = sum(1 for ex in exercise_list if ex['is_completed'])

        percentage = 0
        if total_exercises > 0:
            percentage = int((completed_exercises / total_exercises) * 100)

        context['progress'] = {
            'total_exercises': total_exercises,
            'completed_exercises': completed_exercises,
            'percentage': percentage
        }

        return context


class ExerciseDetailView(LoginRequiredMixin, FormView):
    template_name = 'dashboard/exercise_detail.html'
    form_class = SubmissionForm
    login_url = reverse_lazy('login')

    def get_success_url(self):
        return reverse('exercise_detail', kwargs={
            'course_id': self.kwargs['course_id'],
            'exercise_id': self.kwargs['exercise_id']
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the course
        course = get_object_or_404(Course, id=self.kwargs['course_id'])
        context['course'] = course

        # Get the exercise
        exercise = get_object_or_404(Exercise, id=self.kwargs['exercise_id'], course=course)
        context['exercise'] = exercise

        # Get the assignment
        assignment = get_object_or_404(
            Assignment,
            student=self.request.user,
            exercise=exercise
        )
        context['assignment'] = assignment

        # Get the latest submission
        latest_submission = Submission.objects.filter(
            assignment=assignment
        ).order_by('-submitted_at').first()

        context['submission'] = latest_submission

        if latest_submission and latest_submission.is_checked:
            context['feedback'] = {
                'status': 'good' if latest_submission.mark and latest_submission.mark >= 7 else 'bad',
                'comment': latest_submission.feedback,
                'created_at': latest_submission.submitted_at
            }

        # Get next exercise if this one is completed
        if assignment.is_completed:
            next_exercise = Exercise.objects.filter(
                course=course,
                order__gt=exercise.order
            ).order_by('order').first()

            if next_exercise:
                context['next_exercise'] = next_exercise

        return context

    def form_valid(self, form):
        # Get the exercise
        exercise = get_object_or_404(
            Exercise,
            id=self.kwargs['exercise_id'],
            course_id=self.kwargs['course_id']
        )

        # Get the assignment
        assignment = get_object_or_404(
            Assignment,
            student=self.request.user,
            exercise=exercise
        )

        # Create submission
        submission = form.save(commit=False)
        submission.assignment = assignment

        # Handle different exercise types
        exercise_type = exercise.type

        if exercise_type in ['repeat', 'name_picture', 'tongue_twister']:
            if 'audio_answer' in self.request.FILES:
                submission.audio_answer = self.request.FILES['audio_answer']
            if 'video_answer' in self.request.FILES:
                submission.video_answer = self.request.FILES['video_answer']
        elif exercise_type in ['find_sound', 'mark_sound', 'rhyme', 'complete_word', 'stress', 'sound_picture']:
            submission.text_answer = form.cleaned_data.get('text_answer', '')
        elif exercise_type == 'build_word':
            submission.text_answer = form.cleaned_data.get('text_answer', '')

        submission.save()

        messages.success(self.request, 'Ваш ответ успешно отправлен на проверку.')
        return super().form_valid(form)


class SubmitFeedbackView(LoginRequiredMixin, FormView):
    template_name = 'dashboard/submit_feedback.html'
    form_class = FeedbackForm
    login_url = reverse_lazy('login')

    def get_success_url(self):
        return reverse('exercise_detail', kwargs={
            'course_id': self.kwargs['course_id'],
            'exercise_id': self.kwargs['exercise_id']
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the exercise
        exercise = get_object_or_404(
            Exercise,
            id=self.kwargs['exercise_id'],
            course_id=self.kwargs['course_id']
        )
        context['exercise'] = exercise

        # Get the assignment
        assignment = get_object_or_404(
            Assignment,
            id=self.kwargs['assignment_id'],
            student__therapist=self.request.user
        )
        context['assignment'] = assignment

        # Get the submission
        submission = get_object_or_404(
            Submission,
            id=self.kwargs['submission_id'],
            assignment=assignment
        )
        context['submission'] = submission

        return context

    def form_valid(self, form):
        submission = get_object_or_404(Submission, id=self.kwargs['submission_id'])

        # Check if user is the therapist for this submission
        if submission.assignment.therapist != self.request.user:
            messages.error(self.request, 'У вас нет прав для оценки этого задания.')
            return redirect('dashboard')

        # Update submission with feedback
        submission.feedback = form.cleaned_data['feedback']
        submission.mark = form.cleaned_data['mark']
        submission.is_checked = True
        submission.save()

        # Update assignment completion status if mark is good
        if submission.mark and submission.mark >= 7:
            submission.assignment.is_completed = True
            submission.assignment.completed_at = timezone.now()
            submission.assignment.save()

        messages.success(self.request, 'Обратная связь успешно отправлена.')
        return super().form_valid(form)
