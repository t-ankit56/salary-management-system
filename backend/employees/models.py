from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)


class Employee(models.Model):
    employee_code = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="employees")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="employees")
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="employees")

    hire_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
