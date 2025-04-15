from django.db import models


class ChatMessage(models.Model):
    sender = models.ForeignKey('users.User', related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey('users.User', related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        message = f"{self.sender} → {self.receiver}: "
        if len(self.message) <= 15:
            message += f"{self.message}"
        else:
            message += f"{self.message[:15]}..."
        return message

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        db_table = 'chat_messages'
