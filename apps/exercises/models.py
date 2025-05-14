from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='courses/', null=True, blank=True)
    teaser_video = models.FileField(upload_to='courses/videos/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Exercise(models.Model):
    EXERCISE_TYPES = [
        ('repeat', 'Повторение за логопедом'),
        ('find_sound', 'Найди правильный звук'),
        ('build_word', 'Собери слово из слогов'),
        ('mark_sound', 'Отметь, где слышишь звук'),
        ('rhyme', 'Подбери рифму'),
        ('complete_word', 'Закончи слово'),
        ('name_picture', 'Назови, что на картинке'),
        ('stress', 'Укажи ударение'),
        ('tongue_twister', 'Скороговорка'),
        ('sound_picture', 'Связь звук-картинка'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exercises')
    title = models.CharField(max_length=200)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=EXERCISE_TYPES)
    content = models.JSONField(default=dict)  # Для хранения специфичных для типа упражнения данных
    audio = models.FileField(upload_to='exercises/audio/', null=True, blank=True)
    video = models.FileField(upload_to='exercises/video/', null=True, blank=True)
    image = models.ImageField(upload_to='exercises/images/', null=True, blank=True)
    order = models.PositiveIntegerField(default=0)  # Для определения порядка упражнений в курсе

    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"

    class Meta:
        verbose_name = "Упражнение"
        verbose_name_plural = "Упражнения"
        ordering = ['course', 'order']


class Assignment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_assignments')
    therapist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='therapist_assignments')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student} - {self.exercise}"

    class Meta:
        verbose_name = "Назначение"
        verbose_name_plural = "Назначения"
        unique_together = ['student', 'exercise']


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    audio_answer = models.FileField(upload_to='submissions/audio/', null=True, blank=True)
    video_answer = models.FileField(upload_to='submissions/video/', null=True, blank=True)
    text_answer = models.TextField(blank=True)
    file_answer = models.FileField(upload_to='submissions/files/', null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_checked = models.BooleanField(default=False)
    mark = models.PositiveSmallIntegerField(null=True, blank=True)  # Оценка от 1 до 10
    feedback = models.TextField(blank=True)

    def __str__(self):
        return f"Submission for {self.assignment}"

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
