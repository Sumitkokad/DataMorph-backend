

from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import (
    LoginSerializer, RegisterSerializer, 
    PasswordResetSerializer, PasswordResetConfirmSerializer
)
from django.contrib.auth import get_user_model, authenticate
from knox.models import AuthToken
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from .models import Emails
from .forms import EmailForm
from django.core.mail import send_mail, EmailMultiAlternatives
import logging
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.http import require_GET
from django.utils.html import strip_tags

User = get_user_model()

@require_GET
def test_email_view(request):
    subject = 'Test Email from Django'
    message = 'This is a test email to verify SMTP configuration.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [from_email]
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return HttpResponse('Test email sent successfully.')
    except Exception as e:
        logging.getLogger(__name__).error(f"Error sending test email: {e}")
        return HttpResponse(f'Failed to send test email: {e}', status=500)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not uid or not token or not new_password:
            return Response({'error': 'Missing parameters'}, status=400)

        try:
            uid_decoded = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid_decoded)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid uid'}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Invalid or expired token'}, status=400)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password has been reset successfully'}, status=200)

class LoginViewset(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def create(self, request):
        logger = logging.getLogger(__name__)
        logger.info(f"Login request data: {request.data}")
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            logger.info(f"Login attempt with email: {email}")
            user = authenticate(request, username=email, password=password, email=email)
            if user:
                logger.info(f"Authentication successful for email: {email}")
                _, token = AuthToken.objects.create(user)
                logger.info(f"Token created for user {email}: {token}")
                return Response({
                    "user": {
                        "email": user.email,
                        "id": user.id
                    },
                    "token": token
                })
            else:
                logger.warning(f"Authentication failed for email: {email}")
                return Response({"error": "Invalid credentials"}, status=401)
        else:
            logger.error(f"Login serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=400)

class RegisterViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            _, token = AuthToken.objects.create(user)
            return Response({
                "user": serializer.data,
                "token": token
            })
        else:
            return Response(serializer.errors, status=400)

class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        queryset = User.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

class BasicEmailView(FormView, ListView):
    template_name = "content/home.html"
    context_object_name = 'mydata'
    model = Emails
    form_class = EmailForm
    success_url = reverse_lazy('/')

    def get_queryset(self):
        return Emails.objects.all()

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data['email']
        subject = form.cleaned_data['subject']
        message_content = form.cleaned_data.get('message', '')

        html_message = render_to_string("content/email.html", {'message': message_content})
        plain_message = strip_tags(html_message)
        try:
            message = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email]
            )
            message.attach_alternative(html_message, "text/html")
            message.send()
            logger = logging.getLogger(__name__)
            logger.info(f"✅ Email sent to {email}")
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Error sending email to {email}: {e}")

        return super().form_valid(form)




from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import (
    LoginSerializer, RegisterSerializer, 
    PasswordResetSerializer, PasswordResetConfirmSerializer
)
from django.contrib.auth import get_user_model, authenticate
from knox.models import AuthToken
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from .models import Emails
from .forms import EmailForm
from django.core.mail import send_mail, EmailMultiAlternatives
import logging
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.http import require_GET
from django.utils.html import strip_tags

User = get_user_model()

@require_GET
def test_email_view(request):
    subject = 'Test Email from Django'
    message = 'This is a test email to verify SMTP configuration.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [from_email]
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return HttpResponse('Test email sent successfully.')
    except Exception as e:
        logging.getLogger(__name__).error(f"Error sending test email: {e}")
        return HttpResponse(f'Failed to send test email: {e}', status=500)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not uid or not token or not new_password:
            return Response({'error': 'Missing parameters'}, status=400)

        try:
            uid_decoded = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid_decoded)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid uid'}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Invalid or expired token'}, status=400)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password has been reset successfully'}, status=200)

class LoginViewset(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def create(self, request):
        logger = logging.getLogger(__name__)
        logger.info(f"Login request data: {request.data}")
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            logger.info(f"Login attempt with email: {email}")
            user = authenticate(request, username=email, password=password, email=email)
            if user:
                logger.info(f"Authentication successful for email: {email}")
                _, token = AuthToken.objects.create(user)
                logger.info(f"Token created for user {email}: {token}")
                return Response({
                    "user": {
                        "email": user.email,
                        "id": user.id
                    },
                    "token": token
                })
            else:
                logger.warning(f"Authentication failed for email: {email}")
                return Response({"error": "Invalid credentials"}, status=401)
        else:
            logger.error(f"Login serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=400)

class RegisterViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            _, token = AuthToken.objects.create(user)
            return Response({
                "user": serializer.data,
                "token": token
            })
        else:
            return Response(serializer.errors, status=400)

class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        queryset = User.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

class BasicEmailView(FormView, ListView):
    template_name = "content/home.html"
    context_object_name = 'mydata'
    model = Emails
    form_class = EmailForm
    success_url = reverse_lazy('/')

    def get_queryset(self):
        return Emails.objects.all()

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data['email']
        subject = form.cleaned_data['subject']
        message_content = form.cleaned_data.get('message', '')

        html_message = render_to_string("content/email.html", {'message': message_content})
        plain_message = strip_tags(html_message)
        try:
            message = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email]
            )
            message.attach_alternative(html_message, "text/html")
            message.send()
            logger = logging.getLogger(__name__)
            logger.info(f"✅ Email sent to {email}")
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Error sending email to {email}: {e}")

        return super().form_valid(form)

@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        
        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # For security, always return success even if user doesn't exist
            # This prevents attackers from enumerating valid emails
            return JsonResponse({
                'message': 'If an account exists with this email, you will receive a password reset link.',
                'success': True
            }, status=200)

        try:
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            # Frontend URL - adjust if your frontend runs on a different port
            frontend_url = 'http://localhost:5173'
            reset_url = f"{frontend_url}/reset-password/{uid}/{token}"
            
            subject = 'Password Reset Request - BisMit Co'
            
            # Create text email
            text_message = f"""Hi {user.email},

You requested a password reset for your BisMit Co account.

Please click the link below to reset your password:
{reset_url}

This link will expire in 24 hours.

If you didn't request this, please ignore this email.

Thanks,
BisMit Co Team"""
            
            # Create HTML email
            html_message = f"""<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #333;">Password Reset Request</h2>
        <p>Hi {user.email},</p>
        <p>You requested a password reset for your BisMit Co account.</p>
        <p>Please click the button below to reset your password:</p>
        <p style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}" style="background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">
                Reset Password
            </a>
        </p>
        <p>Or copy and paste this link in your browser:</p>
        <p style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; word-break: break-all;">
            {reset_url}
        </p>
        <p><strong>This link will expire in 24 hours.</strong></p>
        <p>If you didn't request this, please ignore this email.</p>
        <br>
        <p>Thanks,<br>BisMit Co Team</p>
    </div>
</body>
</html>"""

            # Send email
            email_message = EmailMultiAlternatives(
                subject=subject,
                body=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email_message.attach_alternative(html_message, "text/html")
            email_message.send()
            
            # Log success
            logging.getLogger(__name__).info(f"Password reset email sent to {user.email}")
            
            return JsonResponse({
                'message': 'If an account exists with this email, you will receive a password reset link.',
                'success': True
            }, status=200)
            
        except Exception as e:
            # Log error
            logging.getLogger(__name__).error(f"Error sending password reset email: {str(e)}")
            
            return JsonResponse({
                'error': 'Failed to send email. Please try again later.',
                'success': False
            }, status=500)
