from django.db import models


class Exercise(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    audio_file = models.FileField(upload_to='exercises/', blank=True, null=True)
    image = models.ImageField(upload_to='exercise_images/', blank=True, null=True)

    def __str__(self):
        return self.title


class Assignment(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    student = models.ForeignKey(
        'apps.User',
        on_delete=models.CASCADE,
        related_name='student_assignments',
        limit_choices_to={'is_student': True}
    )
    therapist = models.ForeignKey(
        'apps.User',
        on_delete=models.CASCADE,
        related_name='therapist_assignments',
        limit_choices_to={'is_therapist': True}
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.exercise.title} → {self.student.get_full_name()}"


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    audio_answer = models.FileField(upload_to='submissions/audio/', blank=True, null=True)
    text_answer = models.TextField(blank=True)
    feedback = models.TextField(blank=True)
    is_checked = models.BooleanField(default=False)
    mark = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.assignment} - Submission"
