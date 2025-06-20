from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import User

@receiver(post_save, sender=User)
def assign_default_role(sender, instance, created, **kwargs):
    """Assign default role when user is created."""
    if created and not instance.role:
        instance.role = 'student'
        instance.save(update_fields=['role'])
        
        # Send welcome email
        send_mail(
            'Welcome to Campus Management System',
            f'Hello {instance.first_name or instance.username},\n\n'
            f'Welcome to our Campus Management System! Your account has been created successfully.\n'
            f'Your role: {instance.get_role_display()}\n\n'
            f'You can now login and start using the system.',
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            fail_silently=True,
        )