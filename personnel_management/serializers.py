from rest_framework import serializers

from personnel_management.models import Department, DepartmentTitles


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
