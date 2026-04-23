# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from django.contrib.auth import views as auth_views
# from . import views

# # DRF Knox and router setup
# router = DefaultRouter()
# router.register('register', views.RegisterViewset, basename='register')
# router.register('login', views.LoginViewset, basename='login')
# router.register('users', views.UserViewset, basename='users')

# # Django REST Password Reset URLs (kept in users app)
# password_reset_patterns = [

# ]

# # URL patterns
# urlpatterns = [
#     # API Authentication (DRF + Knox)
#     path('api/auth/', include(router.urls)),
#     path('api/knox/', include('knox.urls')),
    
#     # REST Password Reset API
#     path('api/password_reset/', include(password_reset_patterns)),
    
#     # Traditional Django Auth Views (templates based)
#     path('password-reset/',
#          auth_views.PasswordResetView.as_view(
#              template_name='users/password_reset_form.html'
#          ), 
#          name='password_reset'),
    
#     path('password-reset/done/',
#          auth_views.PasswordResetDoneView.as_view(
#              template_name='users/password_reset_done.html'
#          ), 
#          name='password_reset_done'),
    
#     path('password-reset-confirm/<uidb64>/<token>/',
#          auth_views.PasswordResetConfirmView.as_view(
#              template_name='users/password_reset_confirm.html'
#          ), 
#          name='password_reset_confirm'),
    
#     path('password-reset-complete/',
#          auth_views.PasswordResetCompleteView.as_view(
#              template_name='users/password_reset_complete.html'
#          ), 
#          name='password_reset_complete'),
    
#     # Custom API endpoints
#     path('api/email/', views.BasicEmailView.as_view(), name='send_email'),
#     path('api/password-reset-email/', 
#          views.PasswordResetEmailView.as_view(), 
#          name='password_reset_email'),
#     path('api/test-email/', views.test_email_view, name='test_email'),
# ]



# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from django.contrib.auth import views as auth_views
# from . import views

# # DRF Knox and router setup
# router = DefaultRouter()
# router.register('register', views.RegisterViewset, basename='register')
# router.register('login', views.LoginViewset, basename='login')
# router.register('users', views.UserViewset, basename='users')

# urlpatterns = [
#     # API Authentication (DRF + Knox)
#     path('api/', include(router.urls)),  # All API routes under /api/
#     path('api/knox/', include('knox.urls')),
    
#     # Custom API endpoints
#     path('api/email/', views.BasicEmailView.as_view(), name='send_email'),
#     path('api/password-reset-email/', views.PasswordResetEmailView.as_view(), name='password_reset_email'),
#     path('api/reset/password_confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
#     path('api/test-email/', views.test_email_view, name='test_email'),
    
#     # Traditional Django Auth Views (templates based)
#     path('password-reset/',
#          auth_views.PasswordResetView.as_view(
#              template_name='users/password_reset_form.html'
#          ), 
#          name='password_reset'),
    
#     path('password-reset/done/',
#          auth_views.PasswordResetDoneView.as_view(
#              template_name='users/password_reset_done.html'
#          ), 
#          name='password_reset_done'),
    
#     path('password-reset-confirm/<uidb64>/<token>/',
#          auth_views.PasswordResetConfirmView.as_view(
#              template_name='users/password_reset_confirm.html'
#          ), 
#          name='password_reset_confirm'),
    
#     path('password-reset-complete/',
#          auth_views.PasswordResetCompleteView.as_view(
#              template_name='users/password_reset_complete.html'
#          ), 
#          name='password_reset_complete'),
# ]




from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from . import views

# DRF Knox and router setup
router = DefaultRouter()
router.register('register', views.RegisterViewset, basename='register')
router.register('login', views.LoginViewset, basename='login')
router.register('users', views.UserViewset, basename='users')

urlpatterns = [
    # API Authentication (DRF + Knox)
    path('api/', include(router.urls)),  # All API routes under /api/
    path('api/knox/', include('knox.urls')),
    
    # Custom API endpoints
    path('api/email/', views.BasicEmailView.as_view(), name='send_email'),
    path('api/password-reset-email/', views.PasswordResetEmailView.as_view(), name='password_reset_email'),
    path('api/reset/password_confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('api/test-email/', views.test_email_view, name='test_email'),
    
    # Traditional Django Auth Views (templates based) - optional
    # You can comment these out if you're only using the API
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset_form.html'
         ), 
         name='password_reset'),
    
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]