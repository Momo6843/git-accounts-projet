from django.db import models
from django.contrib.auth.models import User

class AccountType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Profile(models.Model):
    name = models.CharField(max_length=100)
    account_types = models.ManyToManyField(AccountType)

    def __str__(self):
        return self.name

class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    account_types = models.ManyToManyField(AccountType, through='EmployeeAccountType')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class EmployeeAccountType(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    account_type = models.ForeignKey(AccountType, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.employee} - {self.account_type}"
