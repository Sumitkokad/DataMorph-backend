# from django.db import models
# from django.contrib.auth.models import AbstractUser
# from django.contrib.auth.base_user import BaseUserManager

# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError('Email is required')
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         extra_fields.setdefault('is_active', True)
#         return self.create_user(email, password, **extra_fields)

# class CustomUser(AbstractUser):
#     email = models.EmailField(unique=True)
#     birthday = models.DateField(null=True, blank=True)
#     username = models.CharField(max_length=150, blank=True, null=True)

#     groups = models.ManyToManyField(
#         'auth.Group',
#         verbose_name='groups',
#         blank=True,
#         help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
#         related_name='customuser_set',
#         related_query_name='customuser',
#     )
#     user_permissions = models.ManyToManyField(
#         'auth.Permission',
#         verbose_name='user permissions',
#         blank=True,
#         help_text='Specific permissions for this user.',
#         related_name='customuser_set',
#         related_query_name='customuser',
#     )

#     objects = CustomUserManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []

#     class Meta:
#         app_label = 'my_auth'

#     def __str__(self):
#         return self.email

# class Emails(models.Model):
#     subject = models.CharField(max_length=500)
#     message = models.TextField(max_length=500)
#     email = models.EmailField()
#     created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
#     edited_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         app_label = 'my_auth'

#     def __str__(self):
#         return self.email


from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    """
    Custom User model that uses email instead of username.
    """
    # Remove the username field
    username = None
    # Make email unique and use it as the username field
    email = models.EmailField('email address', unique=True)
    
    USERNAME_FIELD = 'email'  # Use email as the unique identifier
    REQUIRED_FIELDS = []  # Remove email from REQUIRED_FIELDS
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email

class Emails(models.Model):
    email = models.EmailField()
    subject = models.CharField(max_length=255, blank=True, null=True)  # Added subject
    message = models.TextField(blank=True, null=True)  # Added message
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.email} - {self.subject}"