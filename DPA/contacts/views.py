from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Contact
from .forms import ContactForm
from django.views.generic import ListView
from django.views.generic import View
from django.http import JsonResponse


def contact_list(request):
    return render(request, 'contacts/content.html')
    # return Contact.objects.using('postgres').all()


@login_required
def create_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Отримання даних з форми
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            birthday = form.cleaned_data['birthday']
            # Отримання поточного користувача
            user = request.user
            # Створення нового контакту з встановленням ідентифікатора користувача
            Contact.objects.create(first_name=first_name, last_name=last_name, email=email, phone=phone, birthday=birthday, user=user)
            return redirect('contacts:content')
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
            return redirect('contacts:profile')
        return render(request, 'contacts/edit_contact.html', {'form': form, 'contact_id': contact_id})


def delete_contact(request, contact_id):
    if request.method == 'POST':
        contact = Contact.objects.get(id=contact_id)
        contact.delete()
        return redirect('contacts:profile')
    return JsonResponse({'error': 'Invalid request method.'}, status=405)