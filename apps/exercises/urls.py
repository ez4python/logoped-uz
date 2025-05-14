from django.urls import path

from apps.exercises.views import (
    AllCoursesView, EnrollCourseView, CourseDetailView,
    ExerciseDetailView, SubmitFeedbackView
)

urlpatterns = [
    path('all-courses/', AllCoursesView.as_view(), name='all_courses'),
    path('enroll/<int:course_id>/', EnrollCourseView.as_view(), name='enroll_course'),
    path('course/<int:course_id>/', CourseDetailView.as_view(), name='course_detail'),
    path('course/<int:course_id>/exercise/<int:exercise_id>/', ExerciseDetailView.as_view(), name='exercise_detail'),
    path('submit-feedback/<int:course_id>/<int:exercise_id>/<int:assignment_id>/<int:submission_id>/',
         SubmitFeedbackView.as_view(), name='submit_feedback'),
]
