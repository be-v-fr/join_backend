from django.http import StreamingHttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
import asyncio
from .models import AppUser
from .serializers import LoginSerializer, RegistrationSerializer, UserSerializer, AppUserSerializer
from .serializers import AccountActivationSerializer
from .serializers import RequestPasswordResetSerializer, PerformPasswordResetSerializer

users_changed = False

class LoginView(APIView):
    """
    API endpoint for user login.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Authenticates the user and returns a response with authentication data.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            response_data = serializer.save()
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegistrationView(APIView):
    """
    API endpoint for user registration.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Registers a new user, creating a profile and returning response data.
        """
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            response_data = serializer.save()
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
    
class UserView(APIView):
    """
    API endpoint for user profile access.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieves user profile.
        """
        app_user = AppUser.objects.get(user=request.user)
        serializer = AppUserSerializer(instance=app_user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ActivateAccount(APIView):
    """
    Performs account activation and deletes the corresponding account activation object.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Executes the password reset logic.
        """
        global users_changed
        serializer = AccountActivationSerializer(data=request.data)
        if serializer.is_valid():
            response_data = serializer.save()
            users_changed = True
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RequestPasswordReset(APIView):
    """
    Handles password reset requests by creating a password reset object.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Executes the password reset request logic.
        """
        serializer = RequestPasswordResetSerializer(data=request.data) 
        if serializer.is_valid():
            response_data = serializer.save()
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class PerformPasswordReset(APIView):
    """
    Performs password reset and deletes the corresponding password reset object.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Executes the password reset logic.
        """
        serializer = PerformPasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            response_data = serializer.save()
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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