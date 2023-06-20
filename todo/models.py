from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    complete = models.BooleanField(default=False)
    created = models.DateField(blank=True)

    def __str__(self):
        return f'{self.title} - {self.complete} - {self.created} - {self.user}'
    
    class Meta:
        ordering = ['complete']