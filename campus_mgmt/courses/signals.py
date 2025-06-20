from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Enrollment, Result

@receiver(post_save, sender=Enrollment)
def send_enrollment_confirmation(sender, instance, created, **kwargs):
    """Send enrollment confirmation email."""
    if created and instance.is_active:
        send_mail(
            'Course Enrollment Confirmation',
            f'Hello {instance.student.first_name or instance.student.username},\n\n'
            f'You have successfully enrolled in "{instance.course.title}".\n'
            f'Course starts on: {instance.course.start_date}\n'
            f'Teacher: {instance.course.teacher.get_full_name() or instance.course.teacher.username}\n\n'
            f'Good luck with your studies!',
            settings.DEFAULT_FROM_EMAIL,
            [instance.student.email],
            fail_silently=True,
        )

@receiver(post_save, sender=Result)
def send_grade_notification(sender, instance, created, **kwargs):
    """Send grade notification email to student."""
    if created:
        send_mail(
            'New Grade Available',
            f'Hello {instance.student.first_name or instance.student.username},\n\n'
            f'Your assignment "{instance.assignment.title}" has been graded.\n'
            f'Course: {instance.assignment.course.title}\n'
            f'Marks: {instance.marks_obtained}/{instance.assignment.max_marks}\n'
            f'Grade: {instance.grade}\n\n'
            f'Feedback: {instance.feedback}\n\n'
            f'Login to view more details.',
            settings.DEFAULT_FROM_EMAIL,
            [instance.student.email],
            fail_silently=True,
        )