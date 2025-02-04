from django.db import models
from django.core.validators import MaxValueValidator
from users_app.models import AppUser

class CustomContact(models.Model):
    """
    Represents a custom contact related to an AppUser. Stores details like name, email, phone number, and color ID.
    """
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=50, default=None, blank=True, null=True)
    phone = models.CharField(max_length=20, default=None, blank=True, null=True)
    color_id = models.PositiveSmallIntegerField(validators=[MaxValueValidator(24)], default=None, blank=True, null=True)
    app_user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='user_set', default=None, blank=True, null=True)
    contact_user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='contact_set', default=None, blank=True, null=True)
    
    def __str__(self):
        """
        Returns the string representation of the CustomContact, showing the ID and name.
        """
        return f"({self.id}) {self.name}"