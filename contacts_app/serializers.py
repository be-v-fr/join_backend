from rest_framework import serializers
from users_app.models import AppUser
from users_app.serializers import AppUserSerializer
from .models import CustomContact

class CustomContactSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the CustomContact model, linking contacts to AppUsers.
    """
    contact_user = serializers.PrimaryKeyRelatedField(queryset=AppUser.objects.all(), required=False)

    class Meta:
        model = CustomContact
        fields = ['id', 'name', 'email', 'phone', 'color_id', 'contact_user']