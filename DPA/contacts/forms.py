from django import forms
from django.forms.widgets import DateInput
from .models import Contact
from django.core.exceptions import ValidationError
import re


class ContactForm(forms.ModelForm):

    def validate_phone_number(value):
        pattern = r'^0\d{2}-\d{3}-\d{2}-\d{2}$'
        if not re.match(pattern, value):
            raise ValidationError('Invalid phone number format. Use format: 099-999-99-99')

    first_name = forms.CharField(label='First Name', widget=forms.TextInput(attrs={'placeholder': 'e.g. John'}))
    last_name = forms.CharField(label='Last Name', widget=forms.TextInput(attrs={'placeholder': 'e.g. Smith'}))
    phone = forms.CharField(label='Phone', widget=forms.TextInput(attrs={'placeholder': 'Format: 099-999-99-99'}),
                            validators=[validate_phone_number])
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'placeholder': 'Format: name@example.com'}))
    address = forms.CharField(label='Address', widget=forms.TextInput(attrs={'placeholder': 'Type in your address'}))
    birthday = forms.DateField(label='Birthday', widget=DateInput(attrs={'placeholder': 'Format: yyyy-mm-dd'}))

    # def clean(self):
    #     cleaned_data = super().clean()
    #     first_name = cleaned_data.get('first_name')
    #     last_name = cleaned_data.get('last_name')
    #     phone = cleaned_data.get('phone')
    #
    #     if Contact.objects.filter(first_name=first_name, last_name=last_name, phone=phone,
    #                               user_id=self.instance.user).exists():
    #         raise forms.ValidationError(
    #             "Contact with this name and phone number already exists for this user.")
    #
    #     return cleaned_data

    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'phone', 'email', 'address', 'birthday']


def validate_phone_number(value):
    pattern = r'^\+380\d{2}-\d{3}-\d{2}-\d{2}$'
    if not re.match(pattern, value):
        raise ValidationError('Invalid phone number format. Use format: +38099-999-99-99')
