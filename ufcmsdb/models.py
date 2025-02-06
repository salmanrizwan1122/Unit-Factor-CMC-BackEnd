from django.db import models
from datetime import date
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils.timezone import now

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


class CustomUser(AbstractUser):
    age = models.IntegerField( null=True)
    address = models.CharField(max_length=200 ,null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE , null=True)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE , null=True)
    role = models.ManyToManyField(Role, related_name='users', null=True) 
    cnicno = models.BigIntegerField(null=True) 
    profile_pic = models.ImageField(upload_to='profile_pic/', null=True, blank=True)
    monthly_leave_balance = models.IntegerField(default=2)  
    yearly_leave_balance = models.IntegerField(default=24) 
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users')  # Track the creator

    def __str__(self):
        return self.username


class Leave(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='leaves')
    LEAVE_TYPES = [
        ('Sick', 'Sick'),
        ('Maternity', 'Maternity'),
        ('Paternity', 'Paternity'),
        ('Other', 'Other'),
    ]
    leave_type = models.CharField(max_length=100, choices=LEAVE_TYPES)
    leave_from = models.DateField()
    leave_to = models.DateField()
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Pending')
    reason = models.TextField()
    approved_by = models.CharField(max_length=100, blank=True, null=True)
    approved_date = models.DateField(blank=True, null=True)
    approved_time = models.TimeField(blank=True, null=True)
    leave_days = models.IntegerField(default=0)
    leave_balance = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.name} - {self.leave_type} - {self.status}"
        
class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    punch_in_time = models.TimeField(null=True, blank=True)
    punch_out_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent'), ('Half-day', 'Half-day')])
    total_hours_day = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_hours_month = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_hours_week = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_hours_year = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.status}"

class Expense(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    expense_slip = models.ImageField(upload_to='expense_slips/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.description} - {self.amount}"

class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)  # Project name
    deadline = models.DateField()  # Project deadline
    leader = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='led_projects')  # Project leader
    team_members = models.ManyToManyField(CustomUser, related_name='projects')  # All team members
    total_tasks = models.IntegerField(default=0)  # Total number of tasks in the project
    description = models.TextField(null=True, blank=True)  # Project description (optional)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for project creation
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for last update
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_projects')  # Track the creator
    def __str__(self):
        return self.name
class PasswordResetOTP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)  # 6-digit OTP
    created_at = models.DateTimeField(default=now)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP for {self.email}"

class Task(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=200)  # Task name
    description = models.TextField(null=True, blank=True)  # Task description (optional)
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='tasks')  # Task assigned to
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Pending')  # Task status
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    priority = models.CharField(max_length=100, choices=PRIORITY_CHOICES, default='Medium')  # Task priority
    due_date = models.DateField(null=True, blank=True)  # Task due date
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for task creation
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for last update
    updated_by = models.ForeignKey(CustomUser, related_name='updated_tasks', on_delete=models.SET_NULL, null=True, blank=True)  # Task updated by


    def __str__(self):
        return self.name

class Permission(models.Model):
    id = models.AutoField(primary_key=True)
    action = models.CharField(max_length=80)  # e.g., 'view', 'add', 'edit', 'delete'
    module = models.CharField(max_length=80)  # e.g., 'users', 'reports'

    class Meta:
        unique_together = ('action', 'module')  # Ensure unique combinations

    def __str__(self):
        return f"{self.action.capitalize()} {self.module.capitalize()}"
    
    
    
    
    