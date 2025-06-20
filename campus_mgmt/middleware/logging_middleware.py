import logging
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

# Set up logging
logger = logging.getLogger('user_actions')

class UserActionLoggingMiddleware(MiddlewareMixin):
    """Middleware to log user actions."""
    
    def process_request(self, request):
        # Log significant POST requests
        if request.method == 'POST' and request.user.is_authenticated:
            path = request.path
            
            # Log enrollment actions
            if 'enroll' in path or 'withdraw' in path:
                logger.info(f"User {request.user.username} accessed {path}")
            
            # Log submission actions
            elif 'submit' in path:
                logger.info(f"User {request.user.username} making submission at {path}")
            
            # Log course creation/editing
            elif 'courses' in path and ('create' in path or 'edit' in path):
                logger.info(f"User {request.user.username} modifying course at {path}")
        
        return None

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log user login."""
    logger.info(f"User {user.username} logged in from {request.META.get('REMOTE_ADDR', 'unknown IP')}")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout."""
    if user:
        logger.info(f"User {user.username} logged out")