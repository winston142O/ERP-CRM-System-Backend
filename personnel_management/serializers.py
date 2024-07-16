# Dependency imports
from rest_framework import serializers

# Model imports
from personnel_management.models import (
    Employee,
    Department,
    DepartmentTitles
)


class DepartmentTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentTitles
        fields = (
            'id',
            'title_name'
        )


class DepartmentSerializer(serializers.ModelSerializer):
    titles = serializers.SerializerMethodField()

    def get_titles(self, obj):
        titles = DepartmentTitles.objects.filter(department_id=obj.id)
        return DepartmentTitleSerializer(titles, many=True).data

    class Meta:
        model = Department
        fields = (
            'id',
            'department_name',
            'titles',
        )


class EmployeeSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField(read_only=True, source='department.department_name')
    title = serializers.StringRelatedField(read_only=True, source='title.title_name')
    user_id = serializers.StringRelatedField(read_only=True, source='user.id')

    class Meta:
        model = Employee
        fields = (
            'first_name',
            'last_name',
            'user_id',
            'email',
            'title',
            'department',
            # 'supervisor',
            # 'profile_pic_name'
            # 'employment_contract_name',
            # TODO: Add commented options
        )