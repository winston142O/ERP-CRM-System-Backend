from django.urls import path
from .views import (
    EmployeeDropdownOptions,
    EmployeeSearchAPIView
)

urlpatterns = [
    path('dropdown-options/', EmployeeDropdownOptions.as_view(), name='employee_dropdown_opts'),
    path('employees/<int:employee_id>/', EmployeeSearchAPIView.as_view(), name='employee_search'),
]
