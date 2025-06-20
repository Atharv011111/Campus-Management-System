from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='taught_courses'
    )
    credits = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    start_date = models.DateField()
    end_date = models.DateField()
    max_students = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def enrolled_count(self):
        return self.enrollments.count()
    
    def is_full(self):
        return self.enrolled_count() >= self.max_students

class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    max_marks = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['due_date']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Result(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='results'
    )
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='results')
    marks_obtained = models.PositiveIntegerField()
    grade = models.CharField(max_length=2, blank=True)
    feedback = models.TextField(blank=True)
    graded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'assignment')
        ordering = ['-graded_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.assignment.title} - {self.marks_obtained}/{self.assignment.max_marks}"
    
    def save(self, *args, **kwargs):
        # Auto calculate grade based on percentage
        if self.marks_obtained and self.assignment.max_marks:
            percentage = (self.marks_obtained / self.assignment.max_marks) * 100
            if percentage >= 90:
                self.grade = 'A+'
            elif percentage >= 80:
                self.grade = 'A'
            elif percentage >= 70:
                self.grade = 'B'
            elif percentage >= 60:
                self.grade = 'C'
            elif percentage >= 50:
                self.grade = 'D'
            else:
                self.grade = 'F'
        super().save(*args, **kwargs)