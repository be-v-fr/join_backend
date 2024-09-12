from rest_framework import serializers
from django.contrib.auth.models import User
from api.models import Task, Subtask


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email'] 


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    # assigned_to = UserSerializer(read_only=True, many=True)
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), default=UserSerializer(), many=True)
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'assigned_to', 'created_at', 'due', 'prio', 'category', 'status']
        
        
class SubtaskSerializer(serializers.HyperlinkedModelSerializer):
    # task_id = serializers.IntegerField(source='task.id')
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), default=TaskSerializer())
    class Meta:
        model = Subtask
        fields = ['id', 'title', 'status', 'task']