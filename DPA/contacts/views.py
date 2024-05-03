from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Contact
from .forms import ContactForm
from django.views.generic import ListView
from django.views.generic import View
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.db import IntegrityError


def contact_list(request):
    return render(request, 'contacts/content.html')


@login_required
def create_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                phone = form.cleaned_data['phone']
                email = form.cleaned_data['email']
                address = form.cleaned_data['address']
                birthday = form.cleaned_data['birthday']
                user = request.user
                Contact.objects.create(first_name=first_name, last_name=last_name, phone=phone, email=email, address=address, birthday=birthday, user=user)
                return redirect('contacts:content')
            except IntegrityError:
                messages.error(request, 'Contact with the same name and phone number already exists!')
    else:
        form = ContactForm()
    return render(request, 'contacts/create_contact.html', {'form': form})


class ContactListView(ListView):
    model = Contact
    template_name = 'contacts/content.html'
    context_object_name = 'contacts'

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)


class EditContactView(View):
    def get(self, request, contact_id):
        contact = get_object_or_404(Contact, id=contact_id)
        form = ContactForm(instance=contact)
        return render(request, 'contacts/edit_contact.html', {'form': form, 'contact_id': contact_id})

    def post(self, request, contact_id):
        contact = get_object_or_404(Contact, id=contact_id)
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            return redirect('contacts:content')
        return render(request, 'contacts/edit_contact.html', {'form': form, 'contact_id': contact_id})


def delete_contact(request, contact_id):
    if request.method == 'POST':
        contact = Contact.objects.get(id=contact_id)
        contact.delete()
        return redirect('contacts:content')
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def upcoming_birthdays(request):
    birthdays = []
    today = timezone.now().date()
    upcoming_birthdays_contacts = Contact.objects.filter(user_id=request.user)
    for contact in upcoming_birthdays_contacts:
        birthday = contact.birthday.replace(year=today.year)
        difference = birthday - today
        if 0 < difference.days <= 7:
            birthdays.append(contact)
    return render(request, 'contacts/upcoming_birthdays.html', {'birthdays': birthdays})
