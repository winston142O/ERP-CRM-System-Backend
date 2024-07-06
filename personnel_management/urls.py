from django.urls import path
from .views import (
    EmployeeDropdownOptions
)

urlpatterns = [
    path('dropdown-options/', EmployeeDropdownOptions.as_view(), name='employee_dropdown_opts'),
]
