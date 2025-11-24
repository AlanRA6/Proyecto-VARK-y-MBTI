from django.db import models
from django.conf import settings

# Create your models here.
IND_OR_GROUP_CHOICES = [
    ('individual', 'Individual'),
    ('group', 'Group'),
]

class Token(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tokens')
    token = models.CharField(max_length=255)
    token_type = models.CharField(max_length=10, choices=IND_OR_GROUP_CHOICES, default='individual')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.token_type} - {self.token}"
    
    class Meta:
        ordering = ['-created_at']


class Alumno(models.Model):
    nombre = models.CharField(max_length=255, null=True, blank=True)
    grupo = models.ForeignKey(Token, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre}"
    
    class Meta:
        ordering = ['nombre']