# from django.contrib.auth import get_user_model
# User = get_user_model()

# class EmailAuthBackend:
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         email = kwargs.get('email', username)
#         try:
#             user = User.objects.get(email=email)
#             if user.check_password(password):
#                 return user
#         except User.DoesNotExist:
#             return None

#     def get_user(self, user_id):
#         try:
#             return User.objects.get(pk=user_id)
#         except User.DoesNotExist:
#             return None




# from django.contrib.auth import get_user_model
# from django.contrib.auth.backends import ModelBackend

# User = get_user_model()

# class EmailAuthBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         # Try with email first
#         email = kwargs.get('email', username)
        
#         try:
#             user = User.objects.get(email=email)
#             if user.check_password(password):
#                 return user
#         except User.DoesNotExist:
#             return None
#         return None

#     def get_user(self, user_id):
#         try:
#             return User.objects.get(pk=user_id)
#         except User.DoesNotExist:
#             return None


from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailAuthBackend(BaseBackend):
    """
    Custom authentication backend to authenticate users using email.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        # For compatibility, 'username' parameter might contain email
        email = kwargs.get('email', username)
        
        if email is None or password is None:
            return None
        
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None