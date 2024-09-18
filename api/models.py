from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import MaxValueValidator
import datetime
from .utils import PRIORITY, CATEGORY, STATUS_ALL, STATUS_BASE


class Task(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=500)
    assigned_to = models.ManyToManyField(User, default=None, blank=True)
    created_at = models.DateField(default=datetime.date.today)
    due = models.DateField(default=datetime.date.today)
    prio = models.PositiveSmallIntegerField(
        choices=PRIORITY,
        default=1,
    )
    category = models.PositiveSmallIntegerField(
        choices=CATEGORY,
        default=1,
    )
    status = models.PositiveSmallIntegerField(
        choices=STATUS_ALL,
        default=1,
    )
    
    
    def __str__(self):
        return f"({self.id}) {self.title}"
    
    
class Subtask(models.Model):
    title = models.CharField(max_length=30, default=None, blank=True, null=True)
    status = models.PositiveSmallIntegerField(
        choices=STATUS_BASE,
        default=1,
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
    color_id = models.PositiveSmallIntegerField(validators=[MaxValueValidator(24)], default=None, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_set', default=None, blank=True, null=True)
    
    
    def __str__(self):
        return f"({self.id}) {self.name}"