from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.validators import MaxValueValidator
import datetime
from .choices import PRIORITY, MEDIUM, CATEGORY, TECHNICAL_TASK, STATUS_ALL, STATUS_BASE, TO_DO


class AppUser(models.Model):
    """
    Represents an application-specific user, extending the Django User model.
    """
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, default=None, blank=True, null=True)
    color_id = models.PositiveSmallIntegerField(validators=[MaxValueValidator(24)], default=None, blank=True, null=True)
    
        
    def __str__(self):
        """
        Returns the string representation of the AppUser, showing the ID and username.
        """
        return f"({self.id}) {self.user.username}"
    
    
class PasswordReset(models.Model):
    """
    Represents a password reset request by connecting a user's email to a token.
    """
    email = models.EmailField()
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
        
    def __str__(self):
        """
        Returns the string representation of the AppUser, showing the ID and username.
        """
        return f"{self.email} ({self.created_at})"


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
    
    
class CustomContact(models.Model):
    """
    Represents a custom contact related to an AppUser. Stores details like name, email, phone number, and color ID.
    """
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=50, default=None, blank=True, null=True)
    phone = models.CharField(max_length=20, default=None, blank=True, null=True)
    color_id = models.PositiveSmallIntegerField(validators=[MaxValueValidator(24)], default=None, blank=True, null=True)
    app_user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='user_set', default=None, blank=True, null=True)
    
    
    def __str__(self):
        """
        Returns the string representation of the CustomContact, showing the ID and name.
        """
        return f"({self.id}) {self.name}"