from django.contrib import admin
from apps.exercises.models import Course, Assignment


class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)
    inlines = [AssignmentInline]


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'has_media')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    ordering = ('course', 'order')

    def has_media(self, obj):
        if obj.audio and obj.video:
            return "Audio + Video"
        elif obj.audio:
            return "Audio"
        elif obj.video:
            return "Video"
        elif obj.image:
            return "Image"
        else:
            return "Yo‘q"

    has_media.short_description = "Media mavjudligi"
