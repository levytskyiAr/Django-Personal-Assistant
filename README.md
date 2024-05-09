Personal Assistant
is a versatile application that allows users to stay updated with news in the fields of sports, politics, and culture. Additionally, users can create, save, and edit notes, as well as manage contacts. The app provides the ability to upload and download files to and from the server, open, save, and sort them by categories. It also features authentication and authorization functionalities, as well as password recovery.

Features
News Section: Stay informed with the latest news in sports, politics, and culture.
Notes: Create, save, and edit notes.
Contacts: Manage your contacts easily.
File Management: Upload and download files to and from the server, open, save, and sort them by categories.
Authentication: Securely authenticate users to access the app.
Authorization: Control access to different parts of the app based on user roles.
Password Recovery: Allow users to recover their passwords.
Technologies Used
Frontend: HTML, CSS, JavaScript
Backend: Django
Database:PostgreSQL
Authentication: Django Authentication System
File Storage:Google Drive Integration: Uses aiogoogle to integrate with Google Drive for file storage.
Redis Caching: Implements Redis caching for caching heavy data.
Installation
Clone the repository: https://github.com/levytskyiAr/Django-Personal-Assistant.git
Install dependencies: pip install -r requirements.txt
Set up the database: Currently active cloud database, If you need to use a local database-
python manage.py migrate
Run the development server:
python manage.py runserver
Access the app at http://localhost:8000.
Usage
Register a new account or log in with an existing one.
Navigate through the different sections of the app (News, Notes, Contacts, Files).
Stay updated with the latest news or create, save, and edit notes.
Manage your contacts and upload/download files as needed.
Use the authentication and authorization features to control access to the app.
Recover your password if needed.
Support
If you encounter any issues or have any questions, please feel free to contact us at rolmf85@gmail.com