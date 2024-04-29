import os

from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from aiogoogle import Aiogoogle
from django.views import View

from .async_google_drive.helpers import user_creds, client_creds
import aiogoogle
from .forms import FileUploadForm


async def get_filelist_from_drive(request):
    folder_id = '1Q2U0yza0P1yH_l7R4VnIQHcsuyELbkM2'
    documents = {}
    videos = {}
    images = {}
    other = {}

    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        drive_v3 = await aiogoogle.discover("drive", "v3")
        # Use the aiogoogle client to list files
        res = await aiogoogle.as_user(drive_v3.files.list(q=f"'{folder_id}' in parents and trashed=false"),
                                      full_res=True)
        async for page in res:
            for file in page.get("files"):
                mime_type = file.get("mimeType")
                file_info = [file.get('name'), file.get('id')]
                match mime_type.split('/')[0]:
                    case 'application' | 'text':
                        documents[file.get('name')] = file.get('id')
                    case 'video':
                        videos[file.get('name')] = file.get('id')
                    case 'image':
                        images[file.get('name')] = file.get('id')
                    case _:  # Catch all other files
                        other[file.get('name')] = file.get('id')
    return render(request, 'files/async_show_files_list.html', {
        'documents': documents,
        'videos': videos,
        'images': images,
        'other': other
    })


async def open_file(request, file_id):
    path_to_temporary_file = await create_file_with_correct_name(file_id)
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        drive_v3 = await aiogoogle.discover('drive', 'v3')
    await aiogoogle.as_user(
        drive_v3.files.get(fileId=file_id, download_file=path_to_temporary_file, alt='media'), )

    return FileResponse(open(path_to_temporary_file, 'rb'))


async def download_file(request, file_id):
    path_to_temporary_file = await create_file_with_correct_name(file_id)
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        drive_v3 = await aiogoogle.discover('drive', 'v3')
    await aiogoogle.as_user(
        drive_v3.files.get(fileId=file_id, download_file=path_to_temporary_file, alt='media'), )

    response = FileResponse(open(path_to_temporary_file, 'rb'), as_attachment=True)

    return response


async def create_file_with_correct_name(file_id):
    clean_temp_folder()
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        drive_v3 = await aiogoogle.discover("drive", "v3")
        res = await aiogoogle.as_user(drive_v3.files.get(fileId=file_id))
        path = f'files/temporary_folder/{res['name']}'
        fd = os.open(path, os.O_CREAT, 0o666)
        os.close(fd)
        return path


# async def upload_file(path):
#     async with Aiogoogle(user_creds=user_creds) as aiogoogle:
#         drive_v3 = await aiogoogle.discover('drive', 'v3')
#         await aiogoogle.as_user(
#             drive_v3.files.create(upload_file=path)
#         )


class FileUploadView(View):
    async def post(self, request):
        file = request.FILES['file']
        filename = os.path.join('uploads', file.name)
        with open(filename, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Authenticate with Google Drive using aiogoogle
        # Replace with your Client ID and Client Secret
        service = await aiogoogle.AuthenticatedGoogle(client_id='YOUR_CLIENT_ID', client_secret='YOUR_CLIENT_SECRET')

        # Upload the file to Google Drive
        # Replace with your desired folder ID and file name
        folder_id = 'YOUR_FOLDER_ID'
        file_name = 'uploaded_file.txt'
        await service.drive.files.create(
            name=file_name,
            parents=[folder_id],
            media_body=aiogoogle.MediaFileUpload(filename, mimetype='text/plain')
        )

        return HttpResponse('File uploaded successfully')

    def get(self, request):
        return render(request, 'upload_form.html')


def clean_temp_folder():
    folder_path = 'files/temporary_folder'
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        os.unlink(file_path)
