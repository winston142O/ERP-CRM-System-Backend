# Dependency imports
import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# Model imports
from .models import (
    Department
)
from .serializers import DepartmentSerializer

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
