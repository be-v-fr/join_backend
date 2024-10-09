from django.contrib.auth.models import User
from join_backend.serializers import AppUserSerializer
from rest_framework.response import Response
from rest_framework import status


def get_login_response(app_user, token):
    """
    Returns the login reponse as is common for a successful login post request.
    It requires the corresponding AppUser and Token object.
    """
    app_user_serializer = AppUserSerializer(app_user)
    return Response({
        'token': token.key,
        'appUser': app_user_serializer.data,
    })
    
    
def check_email_availability(email):
    """
    Checks if an email is already taken in the user database.
    If the email is taken, it returns a 400 error response.
    """
    user_by_email = User.objects.get(email__exact=email, many=True)
    if user_by_email:
        return Response(
            {'email': 'This email is already registered.'},
            status=status.HTTP_400_BAD_REQUEST
        )