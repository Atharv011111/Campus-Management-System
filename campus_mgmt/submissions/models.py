from django.db import models
from django.conf import settings
from courses.models import Assignment
import os

def submission_file_path(instance, filename):
    return f'submissions/{instance.assignment.course.id}/{instance.assignment.id}/{instance.student.id}/{filename}'

class Submission(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    file = models.FileField(upload_to=submission_file_path)
    content = models.TextField(blank=True, help_text="Optional text submission")
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'assignment')
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"
    
    def filename(self):
        return os.path.basename(self.file.name) if self.file else None