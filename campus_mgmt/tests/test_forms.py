from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.forms import UserRegistrationForm, UserProfileForm
from courses.forms import CourseForm, AssignmentForm
from submissions.forms import SubmissionForm
from datetime import date, datetime, timedelta
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class UserFormsTest(TestCase):
    def test_user_registration_form_valid(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'student',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_user_registration_form_password_mismatch(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'student',
            'password1': 'complexpass123',
            'password2': 'differentpass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_user_profile_form_valid(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'phone': '1234567890',
            'date_of_birth': date(1990, 1, 1)
        }
        form = UserProfileForm(data=form_data, instance=user)
        self.assertTrue(form.is_valid())

class CourseFormsTest(TestCase):
    def test_course_form_valid(self):
        form_data = {
            'title': 'Test Course',
            'description': 'A test course description',
            'credits': 3,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=90),
            'max_students': 30
        }
        form = CourseForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_course_form_invalid_dates(self):
        form_data = {
            'title': 'Test Course',
            'description': 'A test course description',
            'credits': 3,
            'start_date': date.today() + timedelta(days=90),
            'end_date': date.today(),  # End date before start date
            'max_students': 30
        }
        form = CourseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('End date must be after start date', str(form.errors))
    
    def test_assignment_form_valid(self):
        form_data = {
            'title': 'Test Assignment',
            'description': 'A test assignment description',
            'due_date': datetime.now() + timedelta(days=7),
            'max_marks': 100
        }
        form = AssignmentForm(data=form_data)
        self.assertTrue(form.is_valid())

class SubmissionFormsTest(TestCase):
    def test_submission_form_requires_file_or_content(self):
        # Test with neither file nor content
        form_data = {}
        form = SubmissionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Please provide either a file or text content', str(form.errors))
    
    def test_submission_form_valid_with_content(self):
        form_data = {
            'content': 'This is my text submission'
        }
        uploaded_file = SimpleUploadedFile("file.txt", b"file_content")
        form = SubmissionForm(data={'content': 'some content'}, files={'file_field_name': uploaded_file})