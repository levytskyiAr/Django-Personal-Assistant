from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.CharField(max_length=100, required=True, widget=forms.TextInput())
   
    class Meta:
        model = User
        fields = ['username', 'email']

class LoginForm(AuthenticationForm):

    class Meta:
        model = User
        fields = ['username', 'password']

class SearchForm(forms.Form):
    keyword = forms.CharField(label='Keyword', max_length=100)  