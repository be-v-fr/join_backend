from django.http import StreamingHttpResponse
from django.contrib.auth.models import User
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .utils import get_login_response, check_email_availability
import random
import asyncio


from api.models import AppUser, CustomContact, Task, Subtask
from join_backend.serializers import AppUserSerializer, CustomContactSerializer, TaskSerializer, SubtaskSerializer, UserSerializer


tasks_changed = False
subtasks_changed = False
users_changed = False

class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            app_user = AppUser.objects.get(user=user)
            if app_user:
                return get_login_response(app_user=app_user, token=token)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class GuestLoginView(ObtainAuthToken):
    def login_existing_guest(self, username):
        user = User.objects.get(username=username)
        if user and len(user.email) == 0:
            token, created = Token.objects.get_or_create(user=user)
            app_user = AppUser.objects.get(user=user)
            if app_user:
                return get_login_response(app_user=app_user, token=token)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)        

    
    def post(self, request, *args, **kwargs):
        username = request.data['username']
        if len(username) > 0:
            return self.login_existing_guest(username)
        created_guest = User.objects.create(username='temp', password='guestlogin')
        token = Token.objects.create(user=created_guest)
        created_guest.username = token.key
        created_guest.save()
        created_app_user = AppUser.objects.create(user=created_guest)
        return get_login_response(app_user=created_app_user, token=token)


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []
    
    
    def post(self, request, format=None):
        global users_changed
        user_serializer = UserSerializer(data=request.data)
        try:
            email_error_response = check_email_availability(request.data['email'])
            return email_error_response      
        except:
            if user_serializer.is_valid(raise_exception=True):
                created_user = user_serializer.save()
                AppUser.objects.create(user=created_user, color_id=random.randint(0,24))
                users_changed = True
                return Response(user_serializer.data, status=status.HTTP_201_CREATED)
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TasksView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def get(self, request, format=None):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
    
    def post_task_with_subtasks(self, task_serializer, subtasks_data):
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
        task_serializer = TaskSerializer(data=request.data)
        if task_serializer.is_valid():
            post_response = self.post_task_with_subtasks(task_serializer, request.data['subtasks'])
            return post_response
        return Response(task_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def put_task_with_subtasks(task_serializer, subtasks_data):
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
        pk = kwargs.get('pk')
        task = Task.objects.get(id=pk)
        task_serializer = TaskSerializer(task, data=request.data)
        if task_serializer.is_valid():
            put_response = self.put_task_with_subtasks(task_serializer, request.data['subtasks'])
            return put_response
        return Response(task_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, *args, **kwargs):
        global tasks_changed
        pk = kwargs.get('pk')
        if pk:
            task = Task.objects.get(id=pk)
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        tasks_changed = True
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    
class SubtasksView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def get(self, request, format=None):
        subtasks = Subtask.objects.all()
        serializer = SubtaskSerializer(subtasks, many=True)
        return Response(serializer.data)


    def post(self, request, format=None):
        global subtasks_changed
        serializer = SubtaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            subtasks_changed = True
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def put(self, request, *args, **kwargs):
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
        global subtasks_changed
        pk = kwargs.get('pk')
        if pk:
            subtask = Subtask.objects.get(id=pk)
            subtask.delete()
            subtasks_changed = True
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    
class UsersView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def get(self, request, format=None):
        users = AppUser.objects.all()
        serializer = AppUserSerializer(users, many=True)
        return Response(serializer.data)
    
    
class CurrentUserView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def get(self, request, format=None):
        auth_user = User.objects.get(username=request.user.username)
        app_user = AppUser.objects.get(user=auth_user)
        serializer = AppUserSerializer(app_user)
        return Response(serializer.data) 
    
    
class ContactsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def get(self, request, format=None):
        app_user = AppUser.objects.get(user=request.user)
        custom_contacts = CustomContact.objects.filter(app_user=app_user)
        serializer = CustomContactSerializer(custom_contacts, many=True)
        return Response(serializer.data)


    def post(self, request, format=None):
        app_user = AppUser.objects.get(user=request.user)
        request.data['app_user'] = app_user.id
        serializer = CustomContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def put(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        custom_contact = CustomContact.objects.get(id=pk)
        if custom_contact.app_user.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        request.data['app_user'] = custom_contact.app_user.id
        serializer = CustomContactSerializer(custom_contact, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk:
            custom_contact = CustomContact.objects.get(id=pk)
            if custom_contact.app_user.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            custom_contact.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


async def users_stream(request):
    """
    Sends server-sent events to the client.
    """
    async def event_stream():
        global users_changed
        while True:
            await asyncio.sleep(0.1)
            if users_changed:
                yield f'data: \n\n'
                users_changed = False

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


async def tasks_stream(request):
    """
    Sends server-sent events to the client.
    """
    async def event_stream():
        global tasks_changed
        while True:
            await asyncio.sleep(0.1)
            if tasks_changed:
                yield f'data: \n\n'
                tasks_changed = False

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


async def subtasks_stream(request):
    """
    Sends server-sent events to the client.
    """
    async def event_stream():
        global subtasks_changed
        while True:
            await asyncio.sleep(0.1)
            if subtasks_changed:
                yield f'data: \n\n'
                subtasks_changed = False

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')