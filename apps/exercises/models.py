from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="Nomi")
    description = models.TextField(blank=True, verbose_name="Tavsifi")
    image = models.ImageField(upload_to='courses/images/', verbose_name='Rasm')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Kurs"
        verbose_name_plural = "Kurslar"


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments', verbose_name="Kurs")
    title = models.CharField(max_length=200, verbose_name="Topshiriq nomi")
    description = models.TextField(blank=True, verbose_name="Topshiriq tavsifi")
    audio = models.FileField(upload_to='assignments/audio/', null=True, blank=True, verbose_name="Audio")
    video = models.FileField(upload_to='assignments/video/', null=True, blank=True, verbose_name="Video")
    image = models.ImageField(upload_to='assignments/images/', null=True, blank=True, verbose_name="Rasm")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib raqami")

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    class Meta:
        verbose_name = "Topshiriq"
        verbose_name_plural = "Topshiriqlar"
        ordering = ['course', 'order']


class CompletedAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completed_by')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='completed_assignments')
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} completed {self.assignment}"

    class Meta:
        verbose_name = "Bajarilgan topshiriq"
        verbose_name_plural = "Bajarilgan topshiriqlar"
        unique_together = ('user', 'assignment')
