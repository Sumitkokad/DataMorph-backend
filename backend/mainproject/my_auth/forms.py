# from django import forms
# from django.contrib.auth.forms import AuthenticationForm
# from django.utils.translation import gettext_lazy as _




# from django.forms import ModelForm,DateInput
# from .models import *
# from django.contrib.auth.models import User
# from django import forms
# from django.forms import ModelForm
# from .models import Emails


# class EmailForm(ModelForm):
#     email = forms.EmailField(label="Email", required=True)

#     class Meta:
#         model = Emails
#         fields = ['email', 'subject', 'message']


# class AdminEmailAuthenticationForm(AuthenticationForm):
#     username = forms.EmailField(label=_("Email"), max_length=254)

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm
from .models import Emails

class EmailForm(ModelForm):
    class Meta:
        model = Emails
        fields = ['email', 'subject', 'message']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Recipient email'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Email message', 'rows': 4}),
        }

class AdminEmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label=_("Email"), max_length=254)