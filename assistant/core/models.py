from django.db import models


class Provider(models.Model):
    name = models.CharField(max_length=10)          # ube - Se usa para identificar el provider desde el cliente
    description = models.CharField(max_length=100)  # Universidad Bolivariano del Ecuador (UBE)
    url = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Chat(models.Model):
    user_id = models.CharField(max_length=36)  # UUID de Supabase o ID Django como string
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    title = models.CharField(max_length=36, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.id} - User {self.user_id}"

    def set_title_from_first_message(self, first_message):
        max_len = 36
        if len(first_message) <= max_len:
            self.title = first_message
        else:
            self.title = first_message[:max_len-3] + "..."
        self.save()

class ChatHistory(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    from_ai = models.BooleanField(default=False)

    def __str__(self):
        return f"Message {self.id} in Chat {self.chat.id}"
    
    class Meta:
        ordering = ['created_at']

    def save(self, *args, **kwargs):
        is_first_message = self.chat.messages.count() == 0
        super().save(*args, **kwargs)
        if is_first_message and not self.chat.title:
            self.chat.set_title_from_first_message(self.message)
