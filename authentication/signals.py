import logging
from django.dispatch import receiver
from .models import SignUpApprovalQueue
from .tasks import notify_signup_via_email
from django.db.models.signals import post_save
from personnel_management.models import Employee

logger = logging.getLogger(__name__)


@receiver(post_save, sender=SignUpApprovalQueue)
def send_registration_email_notification(sender, instance: SignUpApprovalQueue, created, **kwargs):
    """
    Notify the system administrators that a new user has registered
    """

    if created:
        logger.info(f"New user registration request from {instance.email}")

        # Get the email addresses of the system administrators
        admin_employees = Employee.objects.filter(title__title_name='System Administrator')
        admin_emails = [employee.email for employee in admin_employees if employee.email and employee.email != '']

        # Retrieve the user's information
        new_user_data = {
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'email': instance.email,
        }

        # Send the email
        notify_signup_via_email.delay(admin_emails, new_user_data)
