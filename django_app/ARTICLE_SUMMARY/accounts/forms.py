from .models import User
from django import forms

class UserForm(forms.ModelForm):
    username = forms.CharField(min_length=2, max_length=30)
    password = forms.CharField(min_length=6, max_length=30)
    email = forms.CharField(min_length=8, max_length=30)
    phone_number = forms.IntegerField()

    class Meta():
        model = User
        fields = ('username', 'password', 'email', 'phone_number')
    