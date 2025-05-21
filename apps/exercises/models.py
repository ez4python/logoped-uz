from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    image = models.ImageField(upload_to='courses/images/', verbose_name='Фото')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано в")
    students = models.ManyToManyField(User, blank=True, related_name='Ученики',
                                      related_query_name='enrolled_courses')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments', verbose_name="Курс")
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    audio = models.FileField(upload_to='assignments/audio/', null=True, blank=True, verbose_name="Аудио")
    video = models.FileField(upload_to='assignments/video/', null=True, blank=True, verbose_name="Видео")
    image = models.ImageField(upload_to='assignments/images/', null=True, blank=True, verbose_name="Фото")
    order = models.PositiveIntegerField(default=0, verbose_name="Номер последовательности")

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    class Meta:
        verbose_name = "Задание"
        verbose_name_plural = "Задании"
        ordering = ['course', 'order']


class CompletedAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completed_by')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='completed_assignments')
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} completed {self.assignment}"

    class Meta:
        verbose_name = "Выполненное задание"
        verbose_name_plural = "Выполненные задании"
        unique_together = ('user', 'assignment')
