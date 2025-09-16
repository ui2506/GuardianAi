from django.conf import settings
from django.db import models

class Call(models.Model):
    target = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    risk_level = models.CharField(max_length=20) 
    risk_confidence = models.FloatField(default=0.0)
    explanation = models.TextField(blank=True)
    recommended_action = models.TextField(blank=True)
    reply_to_user = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_taken = models.BooleanField(default=False)

    def __str__(self):
        return f"[{self.risk_level}] {self.target} @ {self.created_at:%Y-%m-%d %H:%M}"
    
class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ("user", "User"),
        ("assistant", "Assistant"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role}): {self.content[:30]}"