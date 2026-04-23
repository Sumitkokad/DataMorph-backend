# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from django.utils.translation import gettext_lazy as _
# from .models import CustomUser
# from .forms import AdminEmailAuthenticationForm
# from django.contrib.admin.forms import AdminAuthenticationForm
# from django.contrib.auth import views as auth_views

# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     model = CustomUser
#     list_display = ('email', 'is_staff', 'is_superuser', 'is_active')
#     ordering = ('email',)
#     search_fields = ('email',)

#     fieldsets = (
#         (None, {'fields': ('email', 'password')}),
#         (_('Personal info'), {'fields': ('birthday',)}),
#         (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#         (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
#     )
    
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active')}
#         ),
#     )

#     # Tell Django admin to use email instead of username
#     filter_horizontal = ('groups', 'user_permissions',)

# # Override the admin login view to use the custom authentication form
# class CustomAdminLoginView(auth_views.LoginView):
#     authentication_form = AdminEmailAuthenticationForm
#     template_name = "admin/login.html"

# # Unregister the default admin login view and register the custom one
# from django.urls import path
# from django.contrib import admin
# from django.urls import re_path

# admin.site.login = CustomAdminLoginView.as_view()

# # Override the admin urls to use the custom login view
# def get_admin_urls(urls):
#     def get_urls():
#         my_urls = [
#             path('login/', CustomAdminLoginView.as_view(), name='login'),
#         ]
#         return my_urls + urls()
#     return get_urls

# admin.site.get_urls = get_admin_urls(admin.site.get_urls)


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User  # Changed from CustomUser to User
from .forms import AdminEmailAuthenticationForm
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import views as auth_views

@admin.register(User)  # Changed from CustomUser to User
class CustomUserAdmin(UserAdmin):
    model = User  # Changed from CustomUser to User
    list_display = ('email', 'is_staff', 'is_superuser', 'is_active')
    ordering = ('email',)
    search_fields = ('email',)

    # Remove 'birthday' field if it doesn't exist in your User model
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ()}),  # Empty if no personal fields
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active')}
        ),
    )

    # Tell Django admin to use email instead of username
    filter_horizontal = ('groups', 'user_permissions',)

# Override the admin login view to use the custom authentication form
class CustomAdminLoginView(auth_views.LoginView):
    authentication_form = AdminEmailAuthenticationForm
    template_name = "admin/login.html"

# Unregister the default admin login view and register the custom one
from django.urls import path
from django.contrib import admin

admin.site.login = CustomAdminLoginView.as_view()

# Override the admin urls to use the custom login view
def get_admin_urls(urls):
    def get_urls():
        my_urls = [
            path('login/', CustomAdminLoginView.as_view(), name='login'),
        ]
        return my_urls + urls()
    return get_urls

admin.site.get_urls = get_admin_urls(admin.site.get_urls)