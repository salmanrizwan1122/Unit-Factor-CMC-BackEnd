from django.db import models
from datetime import date

class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=80)
    permissions = models.ManyToManyField('Permission', related_name='roles')  

    def __str__(self):
        return self.name

class Department(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=80)

    def __str__(self):
        return self.name
class Designation(models.Model):
    id = models.AutoField(primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    department_name = models.CharField(max_length=255)  # Use an appropriate field type
    
    def __str__(self):
        return self.name


class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    age = models.IntegerField()
    address = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE)
    role = models.ManyToManyField(Role, related_name='users') 
    cnicno = models.BigIntegerField() 
    profile_pic = models.ImageField(upload_to='profile_pic/', null=True, blank=True)
    joining_date = models.DateField(default=date.today)
    user_name = models.CharField(max_length=150, unique=True)  # New unique username field

    def __str__(self):
        return self.name

class Expense(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    expense_slip = models.ImageField(upload_to='expense_slips/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.description} - {self.amount}"

class Permission(models.Model):
    id = models.AutoField(primary_key=True)
    action = models.CharField(max_length=80)  # e.g., 'view', 'add', 'edit', 'delete'
    module = models.CharField(max_length=80)  # e.g., 'users', 'reports'

    class Meta:
        unique_together = ('action', 'module')  # Ensure unique combinations

    def __str__(self):
        return f"{self.action.capitalize()} {self.module.capitalize()}"
    