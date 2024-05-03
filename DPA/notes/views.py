from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Tag, Note
from .forms import NoteForm

@login_required
def main(request):
    """
    Main function for displaying the main notes page.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: A response with the index.html template rendered with the page context.

    """
    notes = Note.objects.filter(author=request.user).all()
    paginator = Paginator(notes, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "notes/index.html", {"page_obj": page_obj})


@login_required
def tag(request):
    """
    View function to handle tag creation.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.

    Raises:
        ValueError: If there is an error in the tag creation process.

    """
    if request.method == "POST":
        try:
            name = request.POST["name"]

            if name:
                tl = Tag(name=name, author=request.user)
                tl.save()
                messages.success(request, f"Tag {name} created")

            return redirect(to="/notes/tag/")

        except ValueError as err:
            messages.error(request, err)
            return render(request, "notes/tag.html", {"error": err})

        except IntegrityError:
            err = "Tag already exists, please enter another tag..."
            messages.error(request, err)
            return render(request, "notes/tag.html", {"error": err})

    return render(request, "notes/tag.html", {})


@login_required
def note(request):
    """
    View function for creating a new note or rendering the note form.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect or HttpResponse: The response object.

    Raises:
        None
    """
    if request.method == "POST":
        name = request.POST["name"]
        description = request.POST["description"]
        list_tags = request.POST.getlist("tags")

        if name and description:
            tags = (
                Tag.objects.filter(name__in=list_tags).filter(author=request.user).all()
            )

            note = Note.objects.create(
                name=name, description=description, author=request.user
            )

            for tag in tags.iterator():
                note.tags.add(tag)

            messages.success(request, f"Note {name} created")

        return redirect(to="/notes/note/")

    tags = Tag.objects.filter(author=request.user).all()

    return render(request, "notes/note.html", {"tags": tags})


@login_required
def detail(request, note_id):
    """
    Retrieves the note with the given note_id from the database,
    generates a comma-separated string of tag names associated with the note,
    and renders the detail.html template with the note object as context.

    Args:
        request (HttpRequest): The HTTP request object.
        note_id (int): The ID of the note to retrieve.

    Returns:
        HttpResponse: The rendered detail.html template with the note object as context.
    """
    note = Note.objects.get(pk=note_id)

    note.tag_list = ", ".join([str(name) for name in note.tags.all()])

    return render(request, "notes/detail.html", {"note": note})


@login_required
def set_done(request, note_id):
    """
    View function to set a note as done.

    Args:
        request (HttpRequest): The HTTP request object.
        note_id (int): The ID of the note to set as done.

    Returns:
        HttpResponseRedirect: A redirect response to the note app home page.
    """
    Note.objects.filter(pk=note_id).update(done=True)
    return redirect(to="/notes/")


@login_required
def delete_note(request, note_id):
    """
    Delete a note with the given note_id.

    Args:
        request (HttpRequest): The HTTP request object.
        note_id (int): The ID of the note to delete.

    Returns:
        HttpResponseRedirect: A redirect response to the note app homepage.
    """
    note = Note.objects.get(pk=note_id)
    note.delete()
    return redirect(to="/notes/")


@login_required
def search_note(request):
    """
    View function to search for notes.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object containing the rendered template.

    """
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
def edit_note(request, note_id):
    try:
        note = Note.objects.get(pk=note_id, author=request.user)
        if request.method == "POST":
            form = NoteForm(request.POST, instance=note)
            if form.is_valid():
                form.save()
                messages.success(request, f"Note '{note.name}' updated successfully")
                return redirect('notes:detail', note_id=note_id)
        else:
            form = NoteForm(instance=note)
        return render(request, 'notes/edit_note.html', {'form': form, 'note_id': note_id})
    except Note.DoesNotExist:
        messages.error(request, "Note does not exist or you don't have permission to edit it")
        return redirect('notes:detail', note_id=note_id)