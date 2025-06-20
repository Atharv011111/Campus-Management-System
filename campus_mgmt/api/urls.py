from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Authentication
    path('auth/login/', views.login_view, name='login'),
    
    # Courses
    path('courses/', views.CourseListCreateView.as_view(), name='course_list_create'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    
    # Assignments
    path('courses/<int:course_id>/assignments/', 
         views.AssignmentListCreateView.as_view(), name='assignment_list_create'),
    
    # Enrollments
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('my-enrollments/', views.my_enrollments, name='my_enrollments'),
    
    # Submissions
    path('assignments/<int:assignment_id>/submissions/', 
         views.SubmissionListCreateView.as_view(), name='submission_list_create'),
]