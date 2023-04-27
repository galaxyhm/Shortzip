from .models import User
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class UserForm(forms.ModelForm):
    username = forms.CharField(min_length=2, max_length=30)
    password = forms.CharField(min_length=6, max_length=30)
    email = forms.CharField(min_length=8, max_length=30)

    class Meta():
        model = User
        fields = ('username', 'password', 'email', 'phone_number')
    

class SignupForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
