# Campus Management System (Django )

A Django-based web application to manage students, teachers, courses, enrollments, results, and more. Includes admin panel, APIs, and email support.

## ✅ Features

- Multi-role support: Admin, Student, Teacher
- Course creation & enrollment system
- Assignment upload & submission
- Result generation & viewing
- Django Admin for full control
- REST API endpoints (using DRF)
- Static/media file handling
- Custom forms, views, and middleware
- Unit testing & pagination
  

## 📁 Project Structure
Campus-Management-System/
├── campus/ # Django app
├── campus_management/ # Django project
├── media/ # Uploaded files
├── templates/ # HTML templates
├── static/ # CSS, JS
├── db.sqlite3
└── manage.py


 ## How to run
1)Clone the Repository
- git clone https://github.com/your-username/campus-management-system.git
-cd campus-management-system

2). Create Virtual Environment (Recommended)
-python -m venv venv
-source venv/bin/activate   # On Windows: venv\Scripts\activate

3). Install Required Packages
-pip install django
-pip install djangorestframework
-pip install djangorestframework-simplejwt
-pip install django-cors-headers
-pip install python-decouple

4) Create .env File
-SECRET_KEY=your-very-secret-key
-DEBUG=True

5)Apply Migrations
-python manage.py makemigrations
-python manage.py migrate

6)Create Superuser (for admin login)
-python manage.py createsuperuser

7)Run the Development Server
-python manage.py runserver

8)Then open: http://localhost:8000



