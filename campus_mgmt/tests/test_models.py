from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from courses.models import Course, Enrollment, Assignment, Result
from submissions.models import Submission
from datetime import date, datetime, timedelta

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'role': 'student'
        }
    
    def test_create_user(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'student')
        self.assertTrue(user.is_student())
        self.assertFalse(user.is_teacher())
        self.assertFalse(user.is_admin_user())
    
    def test_user_str_representation(self):
        user = User.objects.create_user(**self.user_data)
        expected_str = f"{user.username} ({user.get_role_display()})"
        self.assertEqual(str(user), expected_str)

class CourseModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher1',
            email='teacher@example.com',
            password='teacherpass',
            role='teacher'
        )
        self.course_data = {
            'title': 'Test Course',
            'description': 'A test course',
            'teacher': self.teacher,
            'credits': 3,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=90),
            'max_students': 30
        }
    
    def test_create_course(self):
        course = Course.objects.create(**self.course_data)
        self.assertEqual(course.title, 'Test Course')
        self.assertEqual(course.teacher, self.teacher)
        self.assertEqual(course.credits, 3)
        self.assertEqual(course.enrolled_count(), 0)
        self.assertFalse(course.is_full())
    
    def test_course_str_representation(self):
        course = Course.objects.create(**self.course_data)
        self.assertEqual(str(course), 'Test Course')

class EnrollmentModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher1',
            email='teacher@example.com',
            password='teacherpass',
            role='teacher'
        )
        self.student = User.objects.create_user(
            username='student1',
            email='student@example.com',
            password='studentpass',
            role='student'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='A test course',
            teacher=self.teacher,
            credits=3,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            max_students=30
        )
    
    def test_create_enrollment(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.course, self.course)
        self.assertTrue(enrollment.is_active)
        self.assertEqual(self.course.enrolled_count(), 1)
    
    def test_enrollment_str_representation(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
        expected_str = f"{self.student.username} - {self.course.title}"
        self.assertEqual(str(enrollment), expected_str)

class AssignmentModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher1',
            email='teacher@example.com',
            password='teacherpass',
            role='teacher'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='A test course',
            teacher=self.teacher,
            credits=3,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            max_students=30
        )
    
    def test_create_assignment(self):
        assignment = Assignment.objects.create(
            course=self.course,
            title='Test Assignment',
            description='A test assignment',
            due_date=datetime.now() + timedelta(days=7),
            max_marks=100
        )
        self.assertEqual(assignment.course, self.course)
        self.assertEqual(assignment.title, 'Test Assignment')
        self.assertEqual(assignment.max_marks, 100)
    
    def test_assignment_str_representation(self):
        assignment = Assignment.objects.create(
            course=self.course,
            title='Test Assignment',
            description='A test assignment',
            due_date=datetime.now() + timedelta(days=7),
            max_marks=100
        )
        expected_str = f"{self.course.title} - {assignment.title}"
        self.assertEqual(str(assignment), expected_str)

class ResultModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher1',
            email='teacher@example.com',
            password='teacherpass',
            role='teacher'
        )
        self.student = User.objects.create_user(
            username='student1',
            email='student@example.com',
            password='studentpass',
            role='student'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='A test course',
            teacher=self.teacher,
            credits=3,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            max_students=30
        )
        self.assignment = Assignment.objects.create(
            course=self.course,
            title='Test Assignment',
            description='A test assignment',
            due_date=datetime.now() + timedelta(days=7),
            max_marks=100
        )
    
    def test_create_result_with_grade_calculation(self):
        result = Result.objects.create(
            student=self.student,
            assignment=self.assignment,
            marks_obtained=85,
            feedback='Good work!'
        )
        self.assertEqual(result.student, self.student)
        self.assertEqual(result.assignment, self.assignment)
        self.assertEqual(result.marks_obtained, 85)
        self.assertEqual(result.grade, 'A')  # 85% should be grade A
    
    def test_grade_calculation_different_scores(self):
        # Test A+ grade (90%+)
        result_a_plus = Result.objects.create(
            student=self.student,
            assignment=self.assignment,
            marks_obtained=95
        )
        self.assertEqual(result_a_plus.grade, 'A+')
        
        # Create another assignment for additional tests
        assignment2 = Assignment.objects.create(
            course=self.course,
            title='Test Assignment 2',
            description='Another test assignment',
            due_date=datetime.now() + timedelta(days=14),
            max_marks=100
        )
        
        # Test F grade (below 50%)
        result_f = Result.objects.create(
            student=self.student,
            assignment=assignment2,
            marks_obtained=40
        )
        self.assertEqual(result_f.grade, 'F')