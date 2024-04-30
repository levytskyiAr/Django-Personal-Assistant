from django.shortcuts import render, redirect
from .models import Contact
from .forms import ContactForm


def contact_list(request):
    return render(request, 'contacts/contacts.html')
    # return Contact.objects.using('postgres').all()


def create_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contact_list')
    else:
        form = ContactForm()
    return render(request, 'contacts/create_contact.html', {'form': form})