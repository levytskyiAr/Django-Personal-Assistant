from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Note
from .forms import NoteForm
from django.views.generic import ListView
from django.http import JsonResponse
from django.views import View


@login_required
def search_note(request):
    if request.method == "GET":
        query = request.GET.get("q")
        notes = Note.objects.filter(
            name__icontains=query, author=request.user
        )
    else:
        notes = []
    return render(
        request, "notes/search_note.html", {"notes": notes}
    )


@login_required
def create_note(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            note = form.cleaned_data['note']
            tags = form.cleaned_data['tags']
            user = request.user
            Note.objects.create(title=title, note=note, tags=tags, user=user)
            return redirect(to='notes:notes')
    else:
        form = NoteForm()
    return render(request, 'notes/create_note.html', {'form': form})


class NoteListView(ListView):
    model = Note
    template_name = 'notes/notes.html'
    context_object_name = 'notes'

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)


def delete_note(request, note_id):
    if request.method == 'POST':
        notes = Note.objects.get(id=note_id)
        notes.delete()
        return redirect('notes:notes')
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


class EditNoteView(View):
    def get(self, request, note_id):
        note = get_object_or_404(Note, id=note_id)
        form = NoteForm(instance=note)
        return render(request, 'notes/edit_note.html', {'form': form, 'note_id': note_id})

    def post(self, request, note_id):
        note = get_object_or_404(Note, id=note_id)
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            return redirect('notes:notes')
        return render(request, 'notes/edit_note.html', {'form': form, 'note_id': note_id})
