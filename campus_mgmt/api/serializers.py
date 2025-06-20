from rest_framework import serializers
from accounts.models import User
from courses.models import Course, Assignment, Enrollment
from submissions.models import Submission

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']

class CourseSerializer(serializers.ModelSerializer):
    teacher = UserSerializer(read_only=True)
    enrolled_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'teacher', 'credits', 
                 'start_date', 'end_date', 'max_students', 'enrolled_count']

class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['title', 'description', 'credits', 'start_date', 'end_date', 'max_students']
    
    def validate(self, data):
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError("End date must be after start date.")
        return data

class AssignmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    
    class Meta:
        model = Assignment
        fields = ['id', 'course', 'title', 'description', 'due_date', 'max_marks', 'created_at']

class AssignmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date', 'max_marks']

class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'enrolled_at', 'is_active']

class SubmissionSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    assignment = AssignmentSerializer(read_only=True)
    filename = serializers.CharField(read_only=True)
    
    class Meta:
        model = Submission
        fields = ['id', 'student', 'assignment', 'file', 'content', 
                 'submitted_at', 'updated_at', 'filename']

class SubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['file', 'content']
    
    def validate(self, data):
        if not data.get('file') and not data.get('content'):
            raise serializers.ValidationError("Please provide either a file or text content.")
        return data