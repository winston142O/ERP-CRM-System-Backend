# Dependency imports
import os
import logging
from celery import shared_task
from django.db import transaction
from .models import SignUpApprovalQueue
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

# Utility imports
from personnel_management.helpers.utils import (
    create_user,
    create_employee
)
from authentication.helpers.utils import send_email

logger = logging.getLogger(__name__)


@shared_task
def notify_signup_via_email(administrator_emails: list[str], user_data: dict) -> None:
    """
    Send a notification email to all system administrators about a new account that
    must be approved and activated.
    """

    mail_subject = 'New Account Requested'
    context = {
        'user_data': user_data,
        'domain': os.getenv('FRONT_END_BASE_URL'),
    }
    send_email('new_account_request.html', context, mail_subject, administrator_emails)
    logger.info(f"Signup notification email sent to {user_data['email']}")


@shared_task
def create_user_and_send_activation_email(approval_request_data: dict, role_data: dict) -> None:
    """
    Create the models (user, employee) for the newly approved user
    and send a notification email to allow account activation.
    """

    with transaction.atomic():
        try:
            su_request_obj = SignUpApprovalQueue.objects.filter(id=approval_request_data['id']).first()

            # Create the user and employee
            email = approval_request_data['email']
            new_user = create_user(approval_request_data)
            employee = create_employee(approval_request_data, role_data, new_user)

            # Generate a token and UID to send to the user
            token = default_token_generator.make_token(new_user)
            uid = urlsafe_base64_encode(force_bytes(new_user.pk))

            # Send the email
            mail_subject = 'Activate Your Account'
            context = {
                'uid': uid,
                'token': token,
                'first_name': new_user.first_name,
                'username': new_user.username,
                'domain': os.getenv('FRONT_END_BASE_URL'),
            }
            send_email('account_activation_email.html', context, mail_subject, [new_user.email])
            logger.info(f"Account activation email sent to {new_user.email}")

            su_request_obj.delete()

        except Exception as e:
            # if su_request_obj:
            #     su_request_obj.approved = False
            #     su_request_obj.save()
            logger.error(f"Error setting up account activation for {email}, error: {e}")
            raise e


@shared_task
def send_account_invite(employee_data: dict, role_data: dict) -> None:
    """
    Send an account invite so that a user can activate their account and sign in.
    Essentially completing the registration process for them.
    """

    with transaction.atomic():
        # Create the user with a provisional username
        employee_data['username'] = f"{employee_data['first_name']}{employee_data['last_name']}".lower()
        new_user = create_user(employee_data)

        # Create the employee
        employee = create_employee(employee_data, role_data, new_user)

        # Generate a token and UID to send to the user
        token = default_token_generator.make_token(new_user)
        uid = urlsafe_base64_encode(force_bytes(new_user.pk))

        # Send the email
        mail_subject = "You've been invited to the ERP System!"
        context = {
            'uid': uid,
            'token': token,
            'first_name': new_user.first_name,
            'username': new_user.username,
            'domain': os.getenv('FRONT_END_BASE_URL'),
        }
        send_email('account_activation_email.html', context, mail_subject, [new_user.email])
        logger.info(f"Account activation email sent to {new_user.email}")


@shared_task
def send_password_reset_email(user: dict, uid: str, token: str, email: str) -> None:
    """ Sends an email to indicate the user that he is able to reset his/her password. """

    mail_subject = 'Password Reset Requested'
    context = {
        'user': user,
        'uid': uid,
        'token': token,
        'domain': os.getenv('FRONT_END_BASE_URL'),
    }
    send_email('password_reset_email.html', context, mail_subject, [email])
    logger.info(f'Password reset email sent to {email}')
