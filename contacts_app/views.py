from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from users_app.models import AppUser
from .models import CustomContact
from .serializers import CustomContactSerializer


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