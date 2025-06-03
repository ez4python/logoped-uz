from django.urls import path
from .views import (
    AllCoursesView,
    EnrollCourseView,
    CourseDetailView,
    MarkAssignmentCompletedView,
    ExerciseDetailView,
)

urlpatterns = [
    path('', AllCoursesView.as_view(), name='all_courses'),
    path('courses/<int:course_id>/enroll/', EnrollCourseView.as_view(), name='enroll_course'),
    path('courses/<int:course_id>/', CourseDetailView.as_view(), name='course_detail'),
    path('assignments/<int:assignment_id>/complete/', MarkAssignmentCompletedView.as_view(),
         name='mark_assignment_completed'),
    path('courses/<int:course_id>/assignments/<int:assignment_id>/', ExerciseDetailView.as_view(),
         name='exercise_detail'),

]
