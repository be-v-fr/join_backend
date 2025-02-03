from rest_framework import serializers
from users_app.models import AppUser
from .models import Task, Subtask

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
        
        
