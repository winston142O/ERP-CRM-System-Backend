# Generated by Django 5.0.6 on 2024-07-06 07:29

"""
Initialize the module by creating the initial role and department needed
along with a basic System Administrator user.
"""

from django.db import migrations


def add_initial_roles(apps, schema_editor):
    department_model = apps.get_model('personnel_management', 'Department')
    title_model = apps.get_model('personnel_management', 'DepartmentTitles')

    # Create the department
    new_department, created = department_model.objects.get_or_create(department_name='Management')

    # Create the title
    title_model.objects.get_or_create(department=new_department, title_name='System Administrator')


def remove_initial_roles(apps, schema_editor):
    department_model = apps.get_model('personnel_management', 'Department')
    title_model = apps.get_model('personnel_management', 'DepartmentTitles')

    department_model.objects.filter(department_name='Administration').delete()
    title_model.objects.filter(title_name='System Administrator').delete()


def add_initial_user(apps, schema_editor):
    django_user = apps.get_model('auth', 'User')
    department_model = apps.get_model('personnel_management', 'Department')
    title_model = apps.get_model('personnel_management', 'DepartmentTitles')
    employee_model = apps.get_model('personnel_management', 'Employee')

    user_data = {
        "username": "admin",
        "first_name": "Sys",
        "last_name": "Admin",
        "password": "admin1234"
    }

    # Create the user
    new_user = django_user.objects.create_user(**user_data)
    new_user.is_superuser = True
    new_user.is_staff = True
    new_user.save()

    # Create an employee and link it to the user
    employee_data = {
        "first_name": new_user.first_name,
        "last_name": new_user.last_name,
        "department": department_model.objects.get(department_name='Management'),
        "title": title_model.objects.get(title_name='System Administrator'),
        "user": new_user
    }
    employee_model.objects.create(**employee_data)


def remove_initial_user(apps, schema_editor):
    django_user = apps.get_model('auth', 'User')
    employee_model = apps.get_model('personnel_management', 'Employee')

    employee_model.objects.all().delete()
    django_user.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('personnel_management', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_initial_roles, remove_initial_roles),
        migrations.RunPython(add_initial_user, remove_initial_user),
    ]
