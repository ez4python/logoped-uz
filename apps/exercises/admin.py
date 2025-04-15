from django.contrib import admin
from apps.exercises.models import Exercise, Assignment, Submission


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'audio_file', 'image')
    search_fields = ('title', 'description')


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('exercise', 'student', 'therapist', 'assigned_at', 'deadline')
    list_filter = ('assigned_at', 'deadline')
    search_fields = ('exercise__title', 'student__first_name', 'therapist__first_name')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'submitted_at', 'is_checked', 'mark')
    list_filter = ('is_checked', 'submitted_at')
    search_fields = ('assignment__exercise__title', 'assignment__student__first_name')
