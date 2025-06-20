from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Course URLs
    path('', views.CourseListView.as_view(), name='course_list'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('create/', views.CourseCreateView.as_view(), name='course_create'),
    path('<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_update'),
    
    # Enrollment URLs
    path('<int:pk>/enroll/', views.enroll_course, name='enroll_course'),
    path('<int:pk>/withdraw/', views.withdraw_course, name='withdraw_course'),
    
    # Assignment URLs
    path('<int:course_pk>/assignments/create/', 
         views.AssignmentCreateView.as_view(), name='assignment_create'),
    path('assignments/<int:pk>/', 
         views.AssignmentDetailView.as_view(), name='assignment_detail'),
    
    # Results URLs
    path('assignments/<int:assignment_pk>/grade/<int:student_pk>/', 
         views.grade_assignment, name='grade_assignment'),
    path('my-results/', views.my_results, name='my_results'),
]