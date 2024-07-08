import os
import logging
from celery import shared_task
from django.db import transaction
from .models import SignUpApprovalQueue
from django.contrib.auth.models import User
from django.utils.encoding import force_bytes
from personnel_management.models import Employee
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

logger = logging.getLogger(__name__)


@shared_task
def notify_signup_via_email(administrator_emails: list[str], user_data: dict) -> None:
    """
    Send a notification email to all system administrators about a new account that
    must be approved and activated.
    """

    mail_subject = 'New Account Requested'
    message = render_to_string('new_account_request.html', {
        'user_data': user_data,
        'domain': os.getenv('FRONT_END_BASE_URL'),
    })
    email = EmailMultiAlternatives(mail_subject, message, to=administrator_emails)
    email.content_subtype = "html"
    email.send()
    logger.info(f"Password reset email sent to {user_data['email']}")

@shared_task
def create_user_and_send_activation_email(approval_request_data: dict, role_data: dict) -> None:
    """
    Create the models (user, employee) for the newly approved user
    and send a notification email to allow account activation.
    """

    with transaction.atomic():
        try:
            su_request_obj = SignUpApprovalQueue.objects.filter(id=approval_request_data['id']).first()

            # Create the user
            temp_password = User.objects.make_random_password()
            new_user = User.objects.create(
                email=approval_request_data['email'],
                first_name=approval_request_data['first_name'],
                last_name=approval_request_data['last_name'],
                username=approval_request_data['username'],
                is_active=False
            )
            new_user.set_password(temp_password)
            new_user.save()

            # Create the employee
            Employee.objects.create(
                user=new_user,
                first_name=approval_request_data['first_name'],
                last_name=approval_request_data['last_name'],
                email=approval_request_data['email'],
                department_id=role_data['department_id'],
                title_id=role_data['title_id'],
            )

            # Generate a token and UID to send to the user
            token = default_token_generator.make_token(new_user)
            uid = urlsafe_base64_encode(force_bytes(new_user.pk))

            # Send the email
            mail_subject = 'Activate Your Account'
            message = render_to_string('account_activation_email.html', {
                'uid': uid,
                'token': token,
                'first_name': approval_request_data['first_name'],
                'username': approval_request_data['username'],
                'domain': os.getenv('FRONT_END_BASE_URL'),
            })
            email = EmailMultiAlternatives(mail_subject, message, to=[approval_request_data['email']])
            email.content_subtype = "html"
            email.send()
            logger.info(f"Account activation email sent to {approval_request_data['email']}")

            su_request_obj.delete()

        except Exception as e:
            logger.error(f"Error setting up account activation for {approval_request_data['email']}, error: {e}")
            if su_request_obj:
                su_request_obj.approved = False
                su_request_obj.save()


@shared_task
def send_password_reset_email(user: dict, uid: str, token: str, email: str) -> None:
    mail_subject = 'Password Reset Requested'
    message = render_to_string('password_reset_email.html', {
        'user': user,
        'uid': uid,
        'token': token,
        'domain': os.getenv('FRONT_END_BASE_URL'),
    })
    email = EmailMultiAlternatives(mail_subject, message, to=[email])
    email.content_subtype = "html"
    email.send()
    logger.info(f'Password reset email sent to {email}')