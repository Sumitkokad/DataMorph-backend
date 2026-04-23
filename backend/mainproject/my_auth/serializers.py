# from rest_framework import serializers
# from django.contrib.auth import get_user_model
# from .models import *


# User = get_user_model()


# class LoginSerializer(serializers.Serializer):
#     email = serializers.EmailField(label="Login")
#     password = serializers.CharField(label="Password")


#     def to_representation(self,instance):
#         ret = super().to_representation(instance)
#         ret.pop('password',None)
#         return ret

# class RegisterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('id', 'email', 'password')
#         extra_kwargs = {'password': {'write_only': True}}

#     def create(self, validated_data):
#         user = User.objects.create_user(**validated_data)
#         return user


# from rest_framework import serializers
# from django.contrib.auth import get_user_model
# from django.contrib.auth.password_validation import validate_password

# User = get_user_model()

# class LoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField()

# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, required=True)
#     password2 = serializers.CharField(write_only=True, required=True)

#     class Meta:
#         model = User
#         fields = ('email', 'password', 'password2')

#     def validate(self, attrs):
#         if attrs['password'] != attrs['password2']:
#             raise serializers.ValidationError({"password": "Passwords do not match."})
#         return attrs

#     def create(self, validated_data):
#         # Remove password2 from validated data
#         validated_data.pop('password2')
        
#         # Create user with email
#         user = User.objects.create_user(
#             email=validated_data['email'],
#             password=validated_data['password']
#         )
#         return user


from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password2')

    def validate(self, attrs):
        # Check if passwords match
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        
        # Check if email already exists
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})
        
        return attrs

    def create(self, validated_data):
        # Remove password2 from validated data
        validated_data.pop('password2')
        
        # Create user with email (no username needed)
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True, 
        required=True,
        validators=[validate_password]
    )
    new_password2 = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Passwords do not match."})
        return attrs

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(
        write_only=True, 
        required=True,
        validators=[validate_password]
    )
    new_password2 = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Passwords do not match."})
        return attrs