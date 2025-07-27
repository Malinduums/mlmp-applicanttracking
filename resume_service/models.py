from django.db import models
from django.contrib.auth.models import User
import os

def resume_upload_path(instance, filename):
    """Generate upload path for resume files"""
    return f'resumes/{instance.user.id}/{filename}'

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=resume_upload_path)
    extracted_text = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def filename(self):
        return os.path.basename(self.file.name)
