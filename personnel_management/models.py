from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    department_name = models.CharField(max_length=50)
    department_supervisor = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.department_name


class Employee(models.Model):
    employee_id = models.IntegerField(primary_key=True, db_index=True, verbose_name='Employee ID')
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=50, verbose_name='First Name')  # Denormalized from 'User' model
    last_name = models.CharField(max_length=50, verbose_name='Last Name')  # Denormalized from 'User' model
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, null=True)
    supervisor = models.ManyToManyField(User, null=True),
    employment_contract_name = models.CharField(max_length=100, null=True)
    profile_pic_name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
