# Dependency imports
import logging
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
from authentication.permission_classes import IsAdminUser

logger = logging.getLogger(__name__)


class EmployeeDropdownOptions(APIView):
    """
    Retrieve all dropdown options relevant to the employee models
    """

    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        # TODO: Add a filtering option

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

    def get(self, request, employee_id: int = None) -> Response:
        if employee_id is None:
            # Get the filtering options from the query parameters:
            option_list = [
                'name',
                'id',
                'title',
                'department'
            ]
            option_vals = {}
            for option in option_list:
                option_vals[option] = request.query_params.get(option)

            return self.get_all_employees(request, option_vals)

        else:
            return self.get_employee_details(request, employee_id)

    def get_all_employees(self, request, options: dict) -> Response:
        # TODO: Finish this functionality
        pass

    def get_employee_details(self, request, employee_id: int) -> Response:
        # Find the employee
        try:
            employee = Employee.objects.get(pk=employee_id)
            serializer = EmployeeSerializer(employee)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Employee.DoesNotExist:
            return Response({'message':f'Employee with ID {employee_id} does not exist...'}, status=status.HTTP_404_NOT_FOUND)
