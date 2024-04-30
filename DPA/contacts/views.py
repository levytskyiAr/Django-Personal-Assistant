from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Contact
from .forms import ContactForm


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
            return redirect('contacts:profile')
    else:
        form = ContactForm()
    return render(request, 'contacts/create_contact.html', {'form': form})