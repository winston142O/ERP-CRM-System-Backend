# Dependency imports
import logging
from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

# Model imports
from .models import (
    Department, Employee
)

# Utility imports
from .serializers import (
    DepartmentSerializer,
    EmployeeSerializer
)
from .serializers import EmployeeSerializer
from .pagination import EmployeeListPagination
from authentication.permission_classes import IsAdminUser

logger = logging.getLogger(__name__)


class EmployeeDropdownOptions(APIView):
    """
    Retrieve all dropdown options relevant to the employee models
    """

    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:

        # TODO: Finish this filtering option
        filtering_options = [
            'titles',
            'departments'
        ]

        options = {}

        departments = Department.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        options['departments'] = serializer.data

        return Response({**options}, status=status.HTTP_200_OK)


class EmployeeSearchAPIView(ListAPIView):
    """
    Retrieve a list of employees (paginated) and filtered by certain parameters, or, a specific employee.
    """

    permission_classes = [IsAuthenticated & IsAdminUser]
    pagination_class = EmployeeListPagination

    def get(self, request) -> Response:

        employee_id = request.GET.get('employee_id')
        if employee_id is None:
            # Get the filtering options from the query parameters:
            option_list = [
                'name',
                'title',
                'department',
                'email'
            ]
            option_vals = {}
            for option in option_list:
                option_vals[option] = request.query_params.get(option)

            employees = self.get_all_employees(request, option_vals)

            # Serialize and paginate the employees
            paginated_queryset = self.paginate_queryset(employees)
            if paginated_queryset is not None:
                serializer = EmployeeSerializer(paginated_queryset, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = EmployeeSerializer(employees, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return self.get_employee_details(request, employee_id)

    def get_all_employees(self, request, options: dict) -> Response:

        employees = Employee.objects.all()

        # Start filtering as per the requested options
        if options.get('name'):
            employees = employees.filter(
                Q(first_name__icontains=options['name']) |
                Q(last_name__icontains=options['name'])
            )
        if options.get('title'):
            employees = employees.filter(title__title_name__icontains=options['title'])
        if options.get('department'):
            employees = employees.filter(department__department_name__icontains=options['department'])
        if options.get('email'):
            employees = employees.filter(email__icontains=options['email'])

        # TODO: Add the option to filter with custom attributes

        return employees

    def get_employee_details(self, request, employee_id: int) -> Response:
        # Find the employee
        try:
            employee = Employee.objects.get(pk=employee_id)
            serializer = EmployeeSerializer(employee)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Employee.DoesNotExist:
            return Response({'message':f'Employee with ID {employee_id} does not exist...'}, status=status.HTTP_404_NOT_FOUND)
