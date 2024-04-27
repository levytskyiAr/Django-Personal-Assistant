from django.http import HttpResponse
from django.shortcuts import render

from .google_drive_connect.gauth import drive


def get_filelist_from_drive(request):
    folder_id = '1Q2U0yza0P1yH_l7R4VnIQHcsuyELbkM2'
    documents = []
    videos = []
    images = []
    other = []  # New list for "Other" category
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()

    for file in file_list:
        mime_type = file["mimeType"]
        file.FetchMetadata(fields='title, embedLink, webContentLink, iconLink')
        file_info = [file['embedLink'], file['webContentLink'], file['iconLink']]
        match mime_type.split('/')[0]:
            case 'application' | 'text':
                documents.append((file['title'], file_info))
            case 'video':
                videos.append((file['title'], file_info))
            case 'image':
                images.append((file['title'], file_info))
            case _:  # Catch all other files
                other.append((file['title'], file_info))

    return render(request, 'files/show_files_list.html', {
        'documents': documents,
        'videos': videos,
        'images': images,
        'other': other,  # Include the "Other" category in the context
    })


def show_image(request, file_id):
    file = drive.CreateFile({'id': file_id})
    file.GetContentFile('some_file')
    return render(request, 'files/show_file.html', context={'file': file})
