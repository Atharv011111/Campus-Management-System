from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Course, Enrollment, Assignment
from datetime import date, datetime, timedelta

User = get_user_model()

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create test users
        self.student = User.objects.create_user(
            username='student1',
            email='student@example.com',
            password='testpass123',
            role='student'
        )
        
        self.teacher = User.objects.create_user(
            username='teacher1',
            email='teacher@example.com',
            password='testpass123',
            role='teacher'
        )
        
        self.admin = User.objects.create_user(
            username='admin1',
            email='admin@example.com',
            password='testpass123',
            role='admin',
            is_staff=True
        )
        
        # Create test course
        self.course = Course.objects.create(
            title='Test Course',
            description='A test course',
            teacher=self.teacher,
            credits=3,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            max_students=30
        )

class HomeViewTest(ViewsTestCase):
    def test_home_view_anonymous(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome to Campus Management System')
    
    def test_home_view_authenticated(self):
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Go to Dashboard')

class AuthViewsTest(ViewsTestCase):
    def test_login_view_get(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
    
    def test_login_view_post_valid(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'student1',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
    
    def test_login_view_post_invalid(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'student1',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')
    
    def test_register_view_get(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register')
    
    def test_register_view_post_valid(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'role': 'student'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='newuser').exists())

class DashboardViewsTest(ViewsTestCase):
    def test_student_dashboard_requires_login(self):
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_student_dashboard_authenticated(self):
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Student Dashboard')
    
    def test_teacher_dashboard_authenticated(self):
        self.client.login(username='teacher1', password='testpass123')
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Teacher Dashboard')
    
    def test_admin_dashboard_authenticated(self):
        self.client.login(username='admin1', password='testpass123')
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Dashboard')

class CourseViewsTest(ViewsTestCase):
    def test_course_list_view(self):
      self.client.login(username='student1', password='testpass123')
      response = self.client.get(reverse('courses:course_list'))
      self.assertEqual(response.status_code, 200)

    
    def test_course_detail_view(self):
     self.client.login(username='student1', password='testpass123')
     response = self.client.get(reverse('courses:course_detail', kwargs={'pk': self.course.pk}))
     self.assertEqual(response.status_code, 200)

    
    def test_course_create_view_requires_teacher_or_admin(self):
        # Test anonymous user
        response = self.client.get(reverse('courses:course_create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test student user
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('courses:course_create'))
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Test teacher user
        self.client.login(username='teacher1', password='testpass123')
        response = self.client.get(reverse('courses:course_create'))
        self.assertEqual(response.status_code, 200)
    
    def test_course_create_post_valid(self):
        self.client.login(username='teacher1', password='testpass123')
        response = self.client.post(reverse('courses:course_create'), {
            'title': 'New Course',
            'description': 'A new test course',
            'credits': 4,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=120),
            'max_students': 25
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertTrue(Course.objects.filter(title='New Course').exists())

class EnrollmentViewsTest(ViewsTestCase):
    def test_enroll_course_requires_student(self):
        # Test anonymous user
        response = self.client.get(reverse('courses:enroll_course', kwargs={'pk': self.course.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test teacher user
        self.client.login(username='teacher1', password='testpass123')
        response = self.client.get(reverse('courses:enroll_course', kwargs={'pk': self.course.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect with error message
    
    def test_enroll_course_student_success(self):
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('courses:enroll_course', kwargs={'pk': self.course.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect after enrollment
        self.assertTrue(Enrollment.objects.filter(student=self.student, course=self.course).exists())
    
    def test_withdraw_course_student_success(self):
        # First enroll the student
        Enrollment.objects.create(student=self.student, course=self.course)
        
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('courses:withdraw_course', kwargs={'pk': self.course.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect after withdrawal
        
        enrollment = Enrollment.objects.get(student=self.student, course=self.course)
        self.assertFalse(enrollment.is_active)