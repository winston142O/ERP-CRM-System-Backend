import logging
from django.contrib.auth.models import User
from personnel_management.models import (
    Employee,
)

logger = logging.getLogger(__name__)


def create_user(user_data: dict) -> User:
    """ Creates a user with a random password to be activated later. """

    # Create the user
    temp_password = User.objects.make_random_password()
    new_user = User.objects.create(
        email=user_data.pop('email'),
        first_name=user_data.pop('first_name'),
        last_name=user_data.pop('last_name'),
        username=user_data.pop('username'),
        is_active=False,
    )

    # Set password and additional parameters
    new_user.set_password(temp_password)
    new_user.save()

    return new_user


def create_employee(employee_data: dict, role_data: dict, user: User) -> Employee:
    """ Creates an employee and links it to its corresponding user. """

    # Create the employee
    employee = Employee.objects.create(
        user=user,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        department_id=role_data['department_id'],
        title_id=role_data['title_id'],
    )

    return employee
