from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from courses.models import Course, Enrollment
from datetime import date, timedelta

User = get_user_model()

class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
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
        
        # Get JWT tokens
        self.student_token = RefreshToken.for_user(self.student).access_token
        self.teacher_token = RefreshToken.for_user(self.teacher).access_token

class AuthAPITest(APITestCase):
    def test_login_api_valid_credentials(self):
        url = reverse('api:login')
        data = {
            'username': 'student1',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_login_api_invalid_credentials(self):
        url = reverse('api:login')
        data = {
            'username': 'student1',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class CourseAPITest(APITestCase):
    def test_course_list_api_anonymous(self):
        url = reverse('api:course_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Course')
    
    def test_course_create_api_teacher(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.teacher_token}')
        url = reverse('api:course_list_create')
        data = {
            'title': 'New API Course',
            'description': 'Created via API',
            'credits': 4,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=120),
            'max_students': 25
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New API Course')
    
    def test_course_create_api_student_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student_token}')
        url = reverse('api:course_list_create')
        data = {
            'title': 'New API Course',
            'description': 'Created via API',
            'credits': 4,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=120),
            'max_students': 25
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_course_detail_api(self):
        url = reverse('api:course_detail', kwargs={'pk': self.course.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Course')

class EnrollmentAPITest(APITestCase):
    def test_enroll_course_api_student(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student_token}')
        url = reverse('api:enroll_course', kwargs={'course_id': self.course.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Enrollment.objects.filter(student=self.student, course=self.course).exists())
    
    def test_enroll_course_api_teacher_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.teacher_token}')
        url = reverse('api:enroll_course', kwargs={'course_id': self.course.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_my_enrollments_api_student(self):
        # First enroll the student
        Enrollment.objects.create(student=self.student, course=self.course)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student_token}')
        url = reverse('api:my_enrollments')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['course']['title'], 'Test Course')
    
    def test_my_enrollments_api_teacher_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.teacher_token}')
        url = reverse('api:my_enrollments')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)