from django.urls import path
from . import views

app_name = 'submissions'

urlpatterns = [
    path('assignment/<int:assignment_pk>/submit/', 
         views.submit_assignment, name='submit_assignment'),
    path('assignment/<int:assignment_pk>/submissions/', 
         views.SubmissionListView.as_view(), name='submission_list'),
    path('assignment/<int:assignment_pk>/submissions/<int:pk>/', 
         views.SubmissionDetailView.as_view(), name='submission_detail'),
    path('my-submissions/', views.my_submissions, name='my_submissions'),
]