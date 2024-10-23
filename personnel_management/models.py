from django.db import models
from django.contrib.auth.models import User

# Utility imports
from PIL import Image
from .constants import EMPLOYEE_PFP_PATH
from erp_system_backend.helpers.classes import Picture
from erp_system_backend.helpers.utils import img_to_base64


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

    def save_profile_pic(self, profile_pic: Picture):
        """ Saves the picture into the appropriate path and updates the profile_pic_name field. """

        # Keep track of the profile picture name
        self.profile_pic_name = profile_pic.name
        self.save()

        # Save the picture into the appropriate path
        profile_pic.save_in_path('' + profile_pic.name)

    def get_profile_pic(self):
        """ Retrieves the picture and returns the base64 representation. """

        profile_pic_name = self.profile_pic_name
        if profile_pic_name:
            # Retrieve the picture from the appropriate path
            profile_pic = Image.open(EMPLOYEE_PFP_PATH + profile_pic_name, 'r')

            # Get the base64 string
            profile_pic_b64 = img_to_base64(profile_pic)

            return profile_pic_b64

        return None

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