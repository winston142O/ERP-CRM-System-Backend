from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    department_name = models.CharField(max_length=50)
    department_supervisor = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.department_name


class DepartmentTitles(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='titles')
    title_name = models.CharField(max_length=50)

    def __str__(self):
        return self.title_name


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=50, verbose_name='First Name')  # Denormalized from 'User' model
    last_name = models.CharField(max_length=50, verbose_name='Last Name')  # Denormalized from 'User' model
    email = models.EmailField(unique=True, verbose_name='Email', null=True)  # Denormalized from 'User' model
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    title = models.ForeignKey(DepartmentTitles, on_delete=models.CASCADE)
    supervisor = models.ManyToManyField(User, null=True),
    employment_contract_name = models.CharField(max_length=100, null=True)
    profile_pic_name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def save(self, *args, **kwargs):
        # Ensure integrity within denormalized fields
        if self.user:
            self.first_name = self.user.first_name
            self.last_name = self.user.last_name
            if self.user.email:
                self.email = self.user.email

        super().save(*args, **kwargs)


class EmployeeCustomAttributes(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    attribute_name = models.CharField(max_length=50)
    attribute_value = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.attribute_name}: {self.attribute_value}"