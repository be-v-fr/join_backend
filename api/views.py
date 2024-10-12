from django.http import StreamingHttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .utils import get_login_response, check_email_availability
import os
import random
import asyncio
from api.models import AppUser, PasswordReset, CustomContact, Task, Subtask
from join_backend.serializers import EmailAuthTokenSerializer, AppUserSerializer, CustomContactSerializer, ResetPasswordRequestSerializer, ResetPasswordSerializer, TaskSerializer, SubtaskSerializer, UserSerializer

User = get_user_model()

tasks_changed = False
subtasks_changed = False
users_changed = False

class LoginView(ObtainAuthToken):
    """
    Handles user login by validating credentials and returning an authentication token.
    """
    serializer_class = EmailAuthTokenSerializer
    
    
    def post(self, request, *args, **kwargs):
        """
        Authenticates the user and returns a token along with app user details.
        """
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        if serializer.is_valid(raise_exception=True):
            user_data = serializer.validated_data['user']
            user = User.objects.get(email=user_data.email)
            token, created = Token.objects.get_or_create(user=user)
            app_user = AppUser.objects.get(user=user)
            if app_user:
                return get_login_response(app_user=app_user, token=token)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class GuestLoginView(ObtainAuthToken):
    """
    Allows guest users to log in by creating or using an existing guest account.
    """
    def login_existing_guest(self, username):
        """
        Logs in an existing guest user by their username and returns a token.
        """
        user = User.objects.get(username=username)
        if user and user.email == 'guest@login.doesNotExist':
            token, created = Token.objects.get_or_create(user=user)
            app_user = AppUser.objects.get(user=user)
            app_user.user.email = ''
            if app_user:
                return get_login_response(app_user=app_user, token=token)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)        

    
    def post(self, request, *args, **kwargs):
        """
        Logs in an existing guest or creates a new guest account, then returns a token.
        """
        username = request.data['username']
        if len(username) > 0:
            return self.login_existing_guest(username)
        created_guest = User.objects.create(username='temp', email='guest@login.doesNotExist', password='guestlogin')
        token = Token.objects.create(user=created_guest)
        created_guest.username = token.key
        created_guest.save()
        created_app_user = AppUser.objects.create(user=created_guest)
        created_app_user.user.email = ''
        return get_login_response(app_user=created_app_user, token=token)


class RegisterView(APIView):
    """
    Handles user registration by creating new users and AppUser objects.
    """
    authentication_classes = []
    permission_classes = []
    
    
    def post(self, request, format=None):
        """
        Registers a new user and checks if the email is available.
        Returns the created user data or errors.
        """
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
        
        
class RequestPasswordReset(APIView):
    """
    Handles password reset requests by creating a password reset object.
    """
    permission_classes = []
    serializer_class = ResetPasswordRequestSerializer

    def post(self, request):
        """
        Executes the password reset request logic.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid:
            email = request.data['email']
            user = User.objects.filter(email__iexact=email).first()
            if user:
                token_generator = PasswordResetTokenGenerator()
                token = token_generator.make_token(user) 
                reset = PasswordReset(email=email, token=token)
                reset.save()
                reset_url = f"{os.environ['PASSWORD_RESET_BASE_URL']}/{token}"

                # Sending reset link via email (commented out for clarity)
                # ... (email sending code)

                return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "User with credentials not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
class ResetPassword(APIView):
    """
    Performs password reset and deletes the corresponding password reset object.
    """
    permission_classes = []
    serializer_class = ResetPasswordSerializer


    def post(self, request, token):
        """
        Executes the password reset logic.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data['new_password']
        confirm_password = serializer.validated_data['confirm_password']
        if new_password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=400)
        reset_obj = PasswordReset.objects.filter(token=token).first()
        if not reset_obj:
            return Response({'error':'Invalid token'}, status=400)
        user = User.objects.filter(email=reset_obj.email).first()
        if user:
            user.set_password(new_password)
            user.save()
            reset_obj.delete()
            return Response({'success':'Password updated'})
        else: 
            return Response({'error':'No user found'}, status=404)


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
    
    
class ContactsView(APIView):
    """
    Manages CRUD operations for the user's custom contacts.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def get(self, request, format=None):
        """
        Returns all custom contacts for the authenticated user.
        """
        app_user = AppUser.objects.get(user=request.user)
        custom_contacts = CustomContact.objects.filter(app_user=app_user)
        serializer = CustomContactSerializer(custom_contacts, many=True)
        return Response(serializer.data)


    def post(self, request, format=None):
        """
        Creates a new custom contact for the authenticated user and returns it.
        """
        app_user = AppUser.objects.get(user=request.user)
        request.data['app_user'] = app_user.id
        serializer = CustomContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def put(self, request, *args, **kwargs):
        """
        Updates an existing custom contact for the authenticated user.
        """
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
        """
        Deletes a custom contact by its primary key and returns an appropriate status.
        """
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
    Sends empty events to the client for user data update notifications.
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
    Sends empty events to the client for task data update notifications.
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
    Sends empty events to the client for subtask data update notifications.
    """
    async def event_stream():
        global subtasks_changed
        while True:
            await asyncio.sleep(0.1)
            if subtasks_changed:
                yield f'data: \n\n'
                subtasks_changed = False


    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')