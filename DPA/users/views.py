from django import forms
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.views import View
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout

from .forms import RegisterForm


def index(request):
    return render(request, 'users/index.html')

def profile(request):
    return render(request, 'users/profile.html')

class RegisterView(View):
    template_name = 'users/register.html'
    form_class = RegisterForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(to='/')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, context={'form': self.form_class})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            messages.success(request, f'Greetings {username}, your account has been successfully registered')
            return redirect(to='users:login')
        return render(request, self.template_name, context={'form': form})


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    error_messages = {
        'invalid_login': "Invalid username or password. Please try again.",
        'inactive': "This account is inactive.",
    }

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(self.error_messages['invalid_login'], code='invalid_login')
            elif not self.user_cache.is_active:
                raise forms.ValidationError(self.error_messages['inactive'], code='inactive')

        return self.cleaned_data


class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = LoginForm
    success_url = 'profile/'


def change_password(request):
    template_name = 'users/change_password.html'
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been successfully changed!')
            return redirect('/accounts/profile/')
        else:
            messages.error(request, 'The old or new password is not valid.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, template_name, {'form': form})


def logout_view(request):
    logout(request)
    return redirect('/')