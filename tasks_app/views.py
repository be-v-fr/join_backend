from django.http import StreamingHttpResponse
from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import asyncio
from users_app.models import AppUser
from users_app.serializers import AppUserSerializer
from users_app.utils import get_cors_streaming_response, get_preflight_response
from .models import Task, Subtask
from .serializers import TaskSerializer, SubtaskSerializer

tasks_changed = False
subtasks_changed = False

class TasksView(APIView):
    """
    Manages CRUD operations for tasks and their associated subtasks.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, format=None):
        """
        Returns all tasks in the system.
        """
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
    def post_task_with_subtasks(self, task_serializer, subtasks_data):
        """
        Creates a task along with its subtasks and returns the created task.
        """
        global tasks_changed
        global subtasks_changed
        created_task = task_serializer.save()
        tasks_changed = True
        for subtask_data in subtasks_data:
            subtask_data['task'] = created_task.id
            subtask_serializer = SubtaskSerializer(data=subtask_data)
            if subtask_serializer.is_valid():
                subtask_serializer.save()
            else:
                return Response(subtask_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            subtasks_changed = True
        return Response(task_serializer.data, status=status.HTTP_201_CREATED)

    def post(self, request, format=None):
        """
        Creates a new task with subtasks and returns the created task.
        """
        task_serializer = TaskSerializer(data=request.data)
        if task_serializer.is_valid():
            post_response = self.post_task_with_subtasks(task_serializer, request.data['subtasks'])
            return post_response
        return Response(task_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put_task_with_subtasks(self, task_serializer, subtasks_data):
        """
        Updates a task and its subtasks, then returns the updated task.
        """
        global tasks_changed
        global subtasks_changed        
        task_serializer.save()
        tasks_changed = True
        for subtask_data in subtasks_data:
            if subtask_data.get('id'):
                subtask = Subtask.objects.get(id=subtask_data['id'])
                subtask_serializer = SubtaskSerializer(subtask, data=subtask_data)
                if subtask_serializer.is_valid():
                    subtask_serializer.save()
                else:
                    return Response(subtask_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            subtasks_changed = True
        return Response(task_serializer.data)    

    def put(self, request, *args, **kwargs):
        """
        Updates an existing task and its subtasks.
        """
        pk = kwargs.get('pk')
        task = Task.objects.get(id=pk)
        task_serializer = TaskSerializer(task, data=request.data)
        if task_serializer.is_valid():
            put_response = self.put_task_with_subtasks(task_serializer, request.data['subtasks'])
            return put_response
        return Response(task_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """
        Deletes a task by its primary key and returns an appropriate status.
        """
        global tasks_changed
        pk = kwargs.get('pk')
        if pk:
            task = Task.objects.get(id=pk)
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        tasks_changed = True
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
class SubtasksView(APIView):
    """
    Manages CRUD operations for subtasks.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, format=None):
        """
        Returns all subtasks in the system.
        """
        subtasks = Subtask.objects.all()
        serializer = SubtaskSerializer(subtasks, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """
        Creates a new subtask and returns the created subtask.
        """
        global subtasks_changed
        serializer = SubtaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            subtasks_changed = True
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, *args, **kwargs):
        """
        Updates an existing subtask and returns the updated subtask.
        """
        global subtasks_changed
        pk = kwargs.get('pk')
        subtask = Subtask.objects.get(id=pk)
        serializer = SubtaskSerializer(subtask, data=request.data)
        if serializer.is_valid():
            serializer.save()
            subtasks_changed = True
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """
        Deletes a subtask by its primary key and returns an appropriate status.
        """
        global subtasks_changed
        pk = kwargs.get('pk')
        if pk:
            subtask = Subtask.objects.get(id=pk)
            subtask.delete()
            subtasks_changed = True
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
class UsersView(APIView):
    """
    Returns a list of all app users in the system.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, format=None):
        """
        Returns all app users in the system.
        """
        users = AppUser.objects.all()
        serializer = AppUserSerializer(users, many=True)
        return Response(serializer.data)
    
class CurrentUserView(APIView):
    """
    Returns the currently authenticated app user's details.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, format=None):
        """
        Returns the app user details for the currently authenticated user.
        """
        auth_user = User.objects.get(username=request.user.username)
        app_user = AppUser.objects.get(user=auth_user)
        serializer = AppUserSerializer(app_user)
        return Response(serializer.data) 

async def tasks_stream(request):
    """
    Sends empty events to the client for task data update notifications.
    """
    if request.method == "OPTIONS":
        return get_preflight_response()
    
    async def event_stream():
        global tasks_changed
        while True:
            await asyncio.sleep(0.1)
            if tasks_changed:
                yield f'data: \n\n'
                tasks_changed = False
                
    return get_cors_streaming_response(event_stream())

async def subtasks_stream(request):
    """
    Sends empty events to the client for subtask data update notifications.
    """
    if request.method == "OPTIONS":
        return get_preflight_response()
    
    async def event_stream():
        global subtasks_changed
        while True:
            await asyncio.sleep(0.1)
            if subtasks_changed:
                yield f'data: \n\n'
                subtasks_changed = False

    return get_cors_streaming_response(event_stream())