import random
from rest_framework import serializers
from django.contrib.auth.models import User
from api.models import AppUser, CustomContact, Task, Subtask


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the Django User model, handling user creation and password protection.
    """
    password = serializers.CharField(write_only=True)


    def create(self, validated_data):
        """
        Custom create method to handle user creation with hashed password.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        
        
class AppUserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the AppUser model, linking to the related User model.
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AppUser
        fields = ['id', 'user', 'color_id']
        
        
class ResetPasswordRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset requests.
    """
    email = serializers.EmailField(required=True)
    
    
class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for password resets.
    """
    new_password = serializers.RegexField(
        regex=r'^[A-Za-z\d@$!%*?&]{6,}$',
        write_only=True,
        error_messages={'invalid': ('Password must be at least 6 characters long')})
    confirm_password = serializers.CharField(write_only=True, required=True)


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the Task model, handling task creation and assignment to multiple AppUsers.
    """
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=AppUser.objects.all(), many=True)
    
    
    def create(self, validated_data):
        """
        Custom create method to handle the task creation and assignment to app users.
        """
        app_users_ids = self.initial_data['assigned_to']
        task = Task.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            due=validated_data['due'],
            prio=validated_data['prio'],
            category=validated_data['category'],
            status=validated_data['status'],
        )
        for app_user_id in app_users_ids:
            task.assigned_to.add(AppUser.objects.get(id=app_user_id))
        return task
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'assigned_to', 'created_at', 'due', 'prio', 'category', 'status']
        
        
class SubtaskSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the Subtask model, allowing association with a parent task.
    """
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())
    
    class Meta:
        model = Subtask
        fields = ['id', 'name', 'status', 'task']
        
        
class CustomContactSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the CustomContact model, linking contacts to AppUsers.
    """
    app_user = serializers.PrimaryKeyRelatedField(queryset=AppUser.objects.all(), default=AppUserSerializer())
    
    class Meta:
        model = CustomContact
        fields = ['id', 'app_user', 'name', 'email', 'phone', 'color_id']
        