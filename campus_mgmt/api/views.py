from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from courses.models import Course, Assignment, Enrollment
from submissions.models import Submission
from .serializers import (
    CourseSerializer, CourseCreateSerializer,
    AssignmentSerializer, AssignmentCreateSerializer,
    EnrollmentSerializer, SubmissionSerializer, SubmissionCreateSerializer
)

# Authentication Views
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if username and password:
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                }
            })
        else:
            return Response({'error': 'Invalid credentials'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'error': 'Username and password required'}, 
                       status=status.HTTP_400_BAD_REQUEST)

# Course Views
class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CourseCreateSerializer
        return CourseSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        user = self.request.user
        if not (user.is_teacher() or user.is_admin_user()):
            raise PermissionDenied("Only teachers and admins can create courses.")
        serializer.save(teacher=user)

class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def perform_update(self, serializer):
        course = self.get_object()
        user = self.request.user
        if not (course.teacher == user or user.is_admin_user()):
            raise PermissionDenied("You can only edit your own courses.")
        serializer.save()
    
    def perform_destroy(self, instance):
        user = self.request.user
        if not (instance.teacher == user or user.is_admin_user()):
            raise PermissionDenied("You can only delete your own courses.")
        instance.delete()

# Assignment Views
class AssignmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Assignment.objects.filter(course_id=course_id)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AssignmentCreateSerializer
        return AssignmentSerializer
    
    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs['course_id'])
        user = self.request.user
        if not (course.teacher == user or user.is_admin_user()):
            raise PermissionDenied("Only course teachers can create assignments.")
        serializer.save(course=course)

# Enrollment Views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def enroll_course(request, course_id):
    if not request.user.is_student():
        return Response({'error': 'Only students can enroll in courses.'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    course = get_object_or_404(Course, id=course_id)
    
    if course.is_full():
        return Response({'error': 'Course is full.'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={'is_active': True}
    )
    
    if created:
        return Response({'message': f'Successfully enrolled in {course.title}!'}, 
                       status=status.HTTP_201_CREATED)
    elif not enrollment.is_active:
        enrollment.is_active = True
        enrollment.save()
        return Response({'message': f'Re-enrolled in {course.title}!'})
    else:
        return Response({'message': 'Already enrolled in this course.'}, 
                       status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_enrollments(request):
    if not request.user.is_student():
        return Response({'error': 'Only students can view enrollments.'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    enrollments = Enrollment.objects.filter(
        student=request.user, is_active=True
    ).select_related('course')
    
    serializer = EnrollmentSerializer(enrollments, many=True)
    return Response(serializer.data)

# Submission Views
class SubmissionListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        assignment = get_object_or_404(Assignment, id=self.kwargs['assignment_id'])
        return Submission.objects.filter(assignment=assignment)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SubmissionCreateSerializer
        return SubmissionSerializer
    
    def perform_create(self, serializer):
        assignment = get_object_or_404(Assignment, id=self.kwargs['assignment_id'])
        user = self.request.user
        
        if not user.is_student():
            raise PermissionDenied("Only students can submit assignments.")
        
        # Check enrollment
        if not Enrollment.objects.filter(
            student=user, course=assignment.course, is_active=True
        ).exists():
            raise PermissionDenied("You must be enrolled in this course.")
        
        # Update existing submission or create new one
        submission, created = Submission.objects.get_or_create(
            student=user,
            assignment=assignment,
            defaults=serializer.validated_data
        )
        
        if not created:
            for attr, value in serializer.validated_data.items():
                setattr(submission, attr, value)
            submission.save()
        
        return submission