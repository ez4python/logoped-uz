from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, View
from django.http import JsonResponse

from apps.exercises.models import Course, Assignment, CompletedAssignment


class AllCoursesView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'dashboard/all_courses.html'
    context_object_name = 'courses'
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

        # Annotate with exercise count (assuming Course has related name 'exercises')
        queryset = queryset.annotate(exercises_count=Count('assignments'))

        # Get user's completed assignments
        user_assignments = Assignment.objects.filter(course__in=queryset,
                                                     completed_assignments__user=self.request.user).distinct()
        enrolled_course_ids = set(user_assignments.values_list('course_id', flat=True))

        # Add is_enrolled flag to each course
        for course in queryset:
            course.is_enrolled = course.id in enrolled_course_ids

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'all_courses'
        # Remove categories from context because no category now
        context['search_query'] = self.request.GET.get('search', '')
        return context


class EnrollCourseView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        assignments = Assignment.objects.filter(course=course).order_by('order')

        if not assignments.exists():
            messages.error(request, 'В этом курсе пока нет заданий.')
            return redirect('all_courses')

        # Check if user already enrolled
        existing_assignments = Assignment.objects.filter(
            course=course,
            completed_assignments__user=request.user
        )

        if existing_assignments.exists():
            messages.info(request, 'Вы уже записаны на этот курс.')
            return redirect('course_detail', course_id=course_id)

        # ✅ Foydalanuvchini kursga bog‘lash: birinchi mashqni tayyorlash
        first_assignment = assignments.first()
        CompletedAssignment.objects.create(
            user=request.user,
            assignment=first_assignment
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

        assignments = self.object.assignments.all().order_by('order')

        completed_assignments_ids = set(
            CompletedAssignment.objects.filter(
                user=self.request.user,
                assignment__in=assignments
            ).values_list('assignment_id', flat=True)
        )

        assignment_list = []
        is_previous_completed = True

        for assignment in assignments:
            is_completed = assignment.id in completed_assignments_ids
            is_available = is_previous_completed

            assignment_list.append({
                'id': assignment.id,
                'title': assignment.title,
                'description': assignment.description,
                'is_completed': is_completed,
                'is_available': is_available,
                'audio_url': assignment.audio.url if assignment.audio else None,
                'video_url': assignment.video.url if assignment.video else None,
                'image_url': assignment.image.url if assignment.image else None,
                'order': assignment.order,
            })

            is_previous_completed = is_completed

        context['assignments'] = assignment_list

        total = len(assignments)
        completed = sum(1 for a in assignment_list if a['is_completed'])
        percentage = int((completed / total) * 100) if total > 0 else 0

        context['progress'] = {
            'total': total,
            'completed': completed,
            'percentage': percentage
        }

        return context


class ExerciseDetailView(LoginRequiredMixin, DetailView):
    model = Assignment
    template_name = 'dashboard/exercise_detail.html'
    context_object_name = 'assignment'

    def get_object(self):
        course = get_object_or_404(Course, id=self.kwargs['course_id'])
        return get_object_or_404(Assignment, id=self.kwargs['assignment_id'], course=course)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        course = get_object_or_404(Course, id=self.kwargs['course_id'])
        assignment = self.get_object()

        # Foydalanuvchi bu topshiriqni bajarganmi?
        is_completed = CompletedAssignment.objects.filter(
            user=user,
            assignment=assignment
        ).exists()

        context.update({
            'course': course,
            'is_completed': is_completed,
        })

        return context


class MarkAssignmentCompletedView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def post(self, request, assignment_id):
        assignment = get_object_or_404(Assignment, id=assignment_id)

        completed, created = CompletedAssignment.objects.get_or_create(
            user=request.user,
            assignment=assignment
        )

        if created:
            return JsonResponse({'status': 'success', 'message': 'Assignment marked as completed.'})
        else:
            return JsonResponse({'status': 'info', 'message': 'Assignment already completed.'})
