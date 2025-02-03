from django.db import models
import datetime
from .choices import PRIORITY, MEDIUM, CATEGORY, TECHNICAL_TASK, STATUS_ALL, STATUS_BASE, TO_DO
from users_app.models import AppUser


class Task(models.Model):
    """
    Represents a task with details like title, description, due date, priority, category, and status.
    Tasks can be assigned to multiple AppUsers.
    """
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=500, blank=True, default='')
    assigned_to = models.ManyToManyField(AppUser, default=None, blank=True)
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
        """
        Returns the string representation of the Task, showing the ID and title.
        """
        return f"({self.id}) {self.title}"
    
    
class Subtask(models.Model):
    """
    Represents a subtask that belongs to a specific task. It includes a name and a status.
    """
    name = models.CharField(max_length=30, default=None, blank=True, null=True)
    status = models.CharField(
        max_length=32,
        choices=STATUS_BASE,
        default=TO_DO,
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_set', default=None, blank=True, null=True)
    
    
    def __str__(self):
        """
        Returns the string representation of the Subtask, showing the ID and name.
        """
        return f"({self.id}) {self.name}"