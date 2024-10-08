import random
from rest_framework import serializers
from django.contrib.auth.models import User
from api.models import AppUser, CustomContact, Task, Subtask


class UserSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True)


    def create(self, validated_data):
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
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AppUser
        fields = ['id', 'user', 'color_id']


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=AppUser.objects.all(), many=True)
    
    
    def create(self, validated_data):
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
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())
    class Meta:
        model = Subtask
        fields = ['id', 'name', 'status', 'task']
        
        
class CustomContactSerializer(serializers.HyperlinkedModelSerializer):
    app_user = serializers.PrimaryKeyRelatedField(queryset=AppUser.objects.all(), default=AppUserSerializer())
    
    class Meta:
        model = CustomContact
        fields = ['id', 'app_user', 'name', 'email', 'phone', 'color_id']
        