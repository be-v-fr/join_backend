from rest_framework import serializers
from users_app.models import AppUser
from users_app.serializers import AppUserSerializer
from .models import CustomContact

class CustomContactSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the CustomContact model, linking contacts to AppUsers.
    """
    app_user = serializers.PrimaryKeyRelatedField(queryset=AppUser.objects.all(), default=AppUserSerializer())
    
    class Meta:
        model = CustomContact
        fields = ['id', 'app_user', 'name', 'email', 'phone', 'color_id']