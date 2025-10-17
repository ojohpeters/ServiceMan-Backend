"""
Email utility functions for user-related emails.
Provides reusable functions for sending templated emails with HTML formatting.
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from .tokens import email_verification_token
import logging

logger = logging.getLogger(__name__)


def send_templated_email(subject, template_name, context, recipient_list, fail_silently=False):
    """
    Send an email using HTML template with plain text fallback.
    
    Args:
        subject (str): Email subject line
        template_name (str): Name of the template file (without .html extension)
        context (dict): Context data for template rendering
        recipient_list (list): List of recipient email addresses
        fail_silently (bool): Whether to suppress exceptions
        
    Returns:
        int: Number of successfully delivered messages
    """
    try:
        # Render HTML content
        html_content = render_to_string(f'emails/{template_name}.html', context)
        
        # Create plain text version (strip HTML tags)
        from django.utils.html import strip_tags
        text_content = strip_tags(html_content)
        
        # Create email message
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list
        )
        
        # Attach HTML content
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        result = email.send(fail_silently=fail_silently)
        
        logger.info(f"Email sent successfully to {recipient_list}. Subject: {subject}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_list}. Error: {e}")
        if not fail_silently:
            raise
        return 0


def send_verification_email(user, request):
    """
    Send email verification link to user.
    
    Args:
        user: User instance
        request: HTTP request object (for building absolute URI)
        
    Returns:
        int: Number of successfully delivered messages
    """
    token = email_verification_token.make_token(user)
    uid = user.pk
    
    verification_url = request.build_absolute_uri(
        f'/api/users/verify-email/?uid={uid}&token={token}'
    )
    
    context = {
        'user': user,
        'verification_url': verification_url,
    }
    
    return send_templated_email(
        subject='Verify Your Email - ServiceMan Platform',
        template_name='email_verification',
        context=context,
        recipient_list=[user.email],
        fail_silently=False
    )


def send_password_reset_email(user, request):
    """
    Send password reset link to user.
    
    Args:
        user: User instance
        request: HTTP request object (for building absolute URI)
        
    Returns:
        int: Number of successfully delivered messages
    """
    token = default_token_generator.make_token(user)
    uid = user.pk
    
    reset_url = request.build_absolute_uri(
        f'/api/users/password-reset-confirm/?uid={uid}&token={token}'
    )
    
    context = {
        'user': user,
        'reset_url': reset_url,
    }
    
    return send_templated_email(
        subject='Password Reset Request - ServiceMan Platform',
        template_name='password_reset',
        context=context,
        recipient_list=[user.email],
        fail_silently=False
    )


def send_password_reset_success_email(user, request):
    """
    Send password reset confirmation email to user.
    
    Args:
        user: User instance
        request: HTTP request object (for building absolute URI)
        
    Returns:
        int: Number of successfully delivered messages
    """
    login_url = request.build_absolute_uri('/login/')  # Adjust based on your frontend route
    
    context = {
        'user': user,
        'login_url': login_url,
    }
    
    return send_templated_email(
        subject='Password Reset Successful - ServiceMan Platform',
        template_name='password_reset_success',
        context=context,
        recipient_list=[user.email],
        fail_silently=True  # Don't fail if success email fails
    )


