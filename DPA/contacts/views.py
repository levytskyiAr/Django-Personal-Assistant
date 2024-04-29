from django.shortcuts import render
from .models import Contact


def contact_list(request):
    return render(request, 'contacts/contacts.html')
    # return Contact.objects.using('postgres').all()
