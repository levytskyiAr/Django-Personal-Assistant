import os
from pathlib import Path

from gauth import drive
folder_id = '1Q2U0yza0P1yH_l7R4VnIQHcsuyELbkM2'


# create a new file
def create_and_upload_file(file_name='test.py', file_content='Hey Dude!'):
    try:

        my_file = drive.CreateFile({'title': f'{file_name}'})
        my_file.SetContentString(file_content)
        my_file.Upload()
        print(my_file["id"])

        return f'File {file_name} was uploaded!Have a good day!'
    except Exception as _ex:
        return 'Got some trouble, check your code please!'


#_______________________________________________________________________________________________________________


# Upload dir
def upload_dir(dir_path=''):
    try:
        for file_name in os.listdir(dir_path):
            my_file = drive.CreateFile({'title': f'{file_name}'})
            my_file.SetContentFile(os.path.join(dir_path, file_name))
            my_file.Upload()
            print(my_file["id"])

            print(f'File {file_name} was uploaded!')

        return 'Success!Upload finished!'
    except Exception as _ex:
        return 'Got some trouble, check your code please!'


#_______________________________________________________________________________________________________________


# Create a new file in the folder which exists in Google Drive
def upload_file_to_exist_folder(title: str, content: str | Path, folder__id: str):
    new_file = drive.CreateFile({'title': f'{title}.txt', 'parents': [{'id': folder__id}]})
    # Add some content to the file (optional)
    new_file.SetContentString(content)
    # Upload the file
    new_file.Upload()
    return f'File{new_file["title"]} given id: {new_file["id"]} was uploaded!'


#_______________________________________________________________________________________________________________


# Create a new folder in a  Google Drive
def create_and_upload_empty_folder():
    try:

        my_file = drive.CreateFile({'title': 'my_folder', 'mimeType': 'application/vnd.google-apps.folder'})
        my_file.Upload()

        return f'File {my_file["id"]} was uploaded!'
    except Exception as _ex:
        return 'Got some trouble, check your code please!'


#_______________________________________________________________________________________________________________


# Upload image to specific folder which exists in Google Drive
def upload_image_to_exist_folder(title: str, content: str | Path, folder__id: str):
    # Set the path to your image file
    image_path = content
    # Create GoogleDriveFile instance with the image file and set the parents attribute to the folder ID
    new_image = drive.CreateFile({'title': f'{title}', 'parents': [{'id': folder__id}]})

    # Set the content of the file to the image file
    new_image.SetContentFile(image_path)

    # Upload the image file
    new_image.Upload()
    return f'File {new_image["id"]} was uploaded!'


#_________________________________________________________________________________________________________________


# Get all files from Google Drive
def get_all_files():
    files_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    for file in files_list:
        return f"title: {file['title']}_____id: {file['id']}"


#_____________________________________________________________________________________________________________


# Get files from a specific folder
def get_files_from_folder(id_folder: str):
    files_list = dict()
    file_list = drive.ListFile(({'q': f"'{folder_id}' in parents and trashed=false"})).GetList()

    for file1 in file_list:
        files_list[file1['title']] = file1["id"]
        print(file_list)
    return files_list


#_______________________________________________________________________________________________________________
#Download file from drive
def download_image(file_id):
    file = drive.CreateFile({'id': file_id})
    file.GetContentFile('image.jpg')
    return file
#_______________________________________________________________________________________________________________


if __name__ == '__main__':
    # print(create_and_upload_file(file_name='some_file.py', file_content=''))
    print(upload_dir(dir_path='video_for_download'))
    # print(upload_file_to_exist_folder(title='hello from python', content='Hello World', folder__id=folder_id))
    # print(get_files_from_folder(id_folder=folder_id))
    # print(upload_image_to_exist_folder(title="cat", content="path_to_image", folder__id=folder_id))
