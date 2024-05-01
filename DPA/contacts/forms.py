from django import forms
from django.forms.widgets import DateInput
from .models import Contact
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


class ContactForm(forms.ModelForm):

    def validate_phone_number(value):
        pattern = r'^0\d{2}-\d{3}-\d{2}-\d{2}$'
        if not re.match(pattern, value):
            raise ValidationError('Invalid phone number format. Use format: 099-999-99-99')

    first_name = forms.CharField(label='First Name', widget=forms.TextInput(attrs={'placeholder': 'e.g. John'}))
    last_name = forms.CharField(label='Last Name', widget=forms.TextInput(attrs={'placeholder': 'e.g. Smith'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'placeholder': 'name@example.com'}))
    phone = forms.CharField(label='Phone', widget=forms.TextInput(attrs={'placeholder': '099-999-99-99'}), validators=[validate_phone_number])
    birthday = forms.DateField(label='Birthday', widget=DateInput(attrs={'placeholder': 'yyyy-mm-dd'}))

    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'email', 'phone', 'birthday']


def validate_phone_number(value):
    pattern = r'^\+380\d{2}-\d{3}-\d{2}-\d{2}$'
    if not re.match(pattern, value):
        raise ValidationError('Invalid phone number format. Use format: +38099-999-99-99')
