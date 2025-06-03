from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    image = models.ImageField(upload_to='chat/images/', null=True, blank=True)
    video = models.FileField(upload_to='chat/videos/', null=True, blank=True)
    file = models.FileField(upload_to='chat/files/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ['timestamp']


class HelpRequest(models.Model):
    TOPIC_CHOICES = [
        ('technical', 'Техническая проблема'),
        ('account', 'Вопрос по аккаунту'),
        ('course', 'Вопрос по курсу'),
        ('payment', 'Вопрос по оплате'),
        ('other', 'Другое'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='help_requests')
    topic = models.CharField(max_length=20, choices=TOPIC_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Help request from {self.user} - {self.get_topic_display()}"

    class Meta:
        verbose_name = "Запрос в поддержку"
        verbose_name_plural = "Запросы в поддержку"
