from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import MaxValueValidator
import datetime
from .utils import PRIORITY, MEDIUM, CATEGORY, TECHNICAL_TASK, STATUS_ALL, STATUS_BASE, TO_DO


class Task(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=500, blank=True, default='')
    assigned_to = models.ManyToManyField(User, default=None, blank=True)
    created_at = models.DateField(default=datetime.date.today)
    due = models.DateField(default=datetime.date.today)
    prio = models.CharField(
        max_length=32,
        choices=PRIORITY,
        default=MEDIUM,
    )
    category = models.CharField(
        max_length=32,
        choices=CATEGORY,
        default=TECHNICAL_TASK,
    )
    status = models.CharField(
        max_length=32,
        choices=STATUS_ALL,
        default=TO_DO,
    )
    
    
    def __str__(self):
        return f"({self.id}) {self.title}"
    
    
class Subtask(models.Model):
    title = models.CharField(max_length=30, default=None, blank=True, null=True)
    status = models.CharField(
        max_length=32,
        choices=STATUS_BASE,
        default=TO_DO,
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_set', default=None, blank=True, null=True)
    
    
    def __str__(self):
        return f"({self.id}) {self.title}"
    
    
class AppUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None, blank=True, null=True)
    color_id = models.PositiveSmallIntegerField(validators=[MaxValueValidator(24)], default=None, blank=True, null=True)
    
        
    def __str__(self):
        return f"({self.id}) {self.user.username}"
    
    
class CustomContact(models.Model):
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=20, default=None, blank=True, null=True)
    color_id = models.PositiveSmallIntegerField(validators=[MaxValueValidator(24)], default=None, blank=True, null=True)
    app_user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='user_set', default=None, blank=True, null=True)
    
    
    def __str__(self):
        return f"({self.id}) {self.name}"