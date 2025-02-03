from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils.timezone import now
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .utils import send_account_activation_email, send_password_reset_email
import os
import six
from django.core.validators import MaxValueValidator

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Custom token generator for account activation for better stability and code readability.
    """
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )

class UserAction(models.Model):
    """
    Abstract model connecting a user to a token.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True
        unique_together = ('token', 'user')
        
    def __str__(self):
        return f"{self.user.email} ({self.created_at})"

    def is_token_expired(self):
        """
        Checks token expiration date.
        """
        expiration_time = self.created_at + timedelta(hours=24)
        return now() > expiration_time

    @classmethod
    def create_with_token(cls, user, token_generator_class):
        """
        Creates class instance from respective user by using a token generator.
        """
        token = token_generator_class().make_token(user)
        instance = cls(user=user, token=token)
        instance.save()
        return instance        

    @classmethod
    def delete_all_for_user(cls, user):
        """
        Deletes all class instances for the respective user.
        """
        instances = cls.objects.filter(user=user)
        instances.delete()

class AccountActivation(UserAction):
    """
    Account activation model including user email and token.
    """
    @classmethod
    def create_with_email(cls, user):
        """
        Creates class instance and sends corresponding email to the respective user.
        """
        instance = cls.create_with_token(user, AccountActivationTokenGenerator)
        activation_url = os.environ['FRONTEND_BASE_URL'] + 'activate/' + instance.token
        send_account_activation_email(recipient=instance.user.email, activation_url=activation_url)
        return instance

class PasswordReset(UserAction):
    """
    Password reset model including user email and token.
    """
    @classmethod
    def create_with_email(cls, user):
        """
        Creates class instance and sends corresponding email to the respective user.
        """
        instance = cls.create_with_token(user, PasswordResetTokenGenerator)
        reset_url = os.environ['FRONTEND_BASE_URL'] + 'reset_password/' + instance.token
        send_password_reset_email(recipient=instance.user.email, reset_url=reset_url)
        return instance
    
class AppUser(models.Model):
    """
    Represents an application-specific user, extending the Django User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None, blank=True, null=True)
    color_id = models.PositiveSmallIntegerField(validators=[MaxValueValidator(24)], default=None, blank=True, null=True)
        
    def __str__(self):
        """
        Returns the string representation of the AppUser, showing the ID and username.
        """
        return f"({self.id}) {self.user.username}"