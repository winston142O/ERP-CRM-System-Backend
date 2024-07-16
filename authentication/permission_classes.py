from rest_framework.permissions import BasePermission
from personnel_management.models import Employee
from django.contrib.auth.models import User


class IsAdminUser(BasePermission):
    """
    Allows access to admin users.
    """

    def has_permission(self, request, view):
        user_obj = User.objects.get(username=request.user.username)
        employee = Employee.objects.filter(user=user_obj).first()

        if employee:
            return employee.title.title_name == 'System Administrator'
        else:
            return False
