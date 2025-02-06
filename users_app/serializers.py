from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from .models import AccountActivation, PasswordReset, AppUser
from .utils import get_auth_response_data
import random

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login, handling email and password validation.
    """
    email = serializers.EmailField(max_length=63)
    password = serializers.CharField(max_length=63, write_only=True)
    
    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid credentials.')
        attrs.update(username=user.username)
        user = authenticate(**attrs)
        if not user:
            raise serializers.ValidationError('Invalid credentials.')
        elif not user.is_active:
            raise serializers.ValidationError('Your account is currently inactive. Please check your email.')         
        return attrs
    
    def create(self, validated_data):
        user = User.objects.get(email=validated_data['email'])
        token, created = Token.objects.get_or_create(user=user)
        app_user = AppUser.objects.get(user=user)
        app_user_serializer = AppUserSerializer(app_user)
        return get_auth_response_data(app_user=app_user_serializer.data, token=token)              

class RegistrationSerializer(serializers.Serializer):
    """
    Serializer for user registration, handling email and password validation.
    Also creates user instance and corresponding account activation by email.
    """
    username = serializers.CharField(max_length=63)
    email = serializers.EmailField(max_length=63)
    password = serializers.CharField(max_length=63, write_only=True)
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email is already registered.')
        return value
    
    def validate_password(self, value):
        validate_password(value)
        return value
    
    def create(self, validated_data):
        created_user = User.objects.create_user(**validated_data)
        created_user.is_active = False
        created_user.save()
        AppUser.objects.create(user=created_user, color_id=random.randint(0,24))
        AccountActivation.create_with_email(user=created_user)
        return {'success': 'We have sent you a link to activate your password.'}
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class AccountActivationSerializer(serializers.Serializer):
    """
    Serializer for performing account activation.
    """
    token = serializers.CharField(write_only=True, required=True)
    
    def validate_token(self, value):
        try:
            activation_obj = AccountActivation.objects.get(token=value)
        except AccountActivation.DoesNotExist:
            raise serializers.ValidationError('Invalid token.')
        if activation_obj.is_token_expired():
            activation_obj.user.delete()
            raise serializers.ValidationError('Your token is expired. Please sign up again.')            
        return value
        
    def create(self, validated_data):
        activation_obj = AccountActivation.objects.get(token=validated_data['token'])
        activation_obj.user.is_active = True
        activation_obj.user.save()
        AccountActivation.delete_all_for_user(user=activation_obj.user)
        return {'success':'Account activated.'}

class RequestPasswordResetSerializer(serializers.Serializer):
    """
    Serializer for password reset requests.
    """
    email = serializers.EmailField(write_only=True, required=True)
    
    def create(self, validated_data):
        email = validated_data['email']
        user = User.objects.filter(email__iexact=email).first()
        if user:
            PasswordReset.delete_all_for_user(user=user)
            PasswordReset.create_with_email(user=user)
        return {'success': 'We have sent you a link to reset your password.'}
    
    
class PerformPasswordResetSerializer(serializers.Serializer):
    """
    Serializer for performing password resets.
    """
    new_password = serializers.CharField(max_length=63, write_only=True)
    token = serializers.CharField(write_only=True, required=True)
    
    def validate_new_password(self, value):
        validate_password(value)
        return value
    
    def validate_token(self, value):
        try:
            reset_obj = PasswordReset.objects.get(token=value)
        except PasswordReset.DoesNotExist:
            raise serializers.ValidationError('Invalid token.')
        if reset_obj.is_token_expired():
            reset_obj.delete()
            raise serializers.ValidationError('Your token is expired.')            
        return value
        
    def create(self, validated_data):
        new_password = validated_data['new_password']
        reset_obj = PasswordReset.objects.get(token=validated_data['token'])
        reset_obj.user.set_password(new_password)
        reset_obj.user.save()
        PasswordReset.delete_all_for_user(user=reset_obj.user)
        return {'success':'Password updated.'}
    
class AppUserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the AppUser model, linking to the related User model.
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AppUser
        fields = ['id', 'user', 'color_id']