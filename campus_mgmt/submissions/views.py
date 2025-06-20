from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.utils import timezone
from courses.models import Assignment, Enrollment
from .models import Submission
from .forms import SubmissionForm

@login_required
def submit_assignment(request, assignment_pk):
    assignment = get_object_or_404(Assignment, pk=assignment_pk)
    
    # Check if user is enrolled in the course
    if not request.user.is_student():
        messages.error(request, 'Only students can submit assignments.')
        return redirect('courses:assignment_detail', pk=assignment_pk)
    
    if not Enrollment.objects.filter(
        student=request.user, 
        course=assignment.course, 
        is_active=True
    ).exists():
        messages.error(request, 'You must be enrolled in this course to submit assignments.')
        return redirect('courses:assignment_detail', pk=assignment_pk)
    
    # Check if assignment is still open
    if timezone.now() > assignment.due_date:
        messages.warning(request, 'This assignment is past due date.')
    
    try:
        submission = Submission.objects.get(student=request.user, assignment=assignment)
        is_update = True
    except Submission.DoesNotExist:
        submission = None
        is_update = False
    
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = request.user
            submission.assignment = assignment
            submission.save()
            
            action = 'updated' if is_update else 'submitted'
            messages.success(request, f'Assignment {action} successfully!')
            return redirect('courses:assignment_detail', pk=assignment_pk)
    else:
        form = SubmissionForm(instance=submission)
    
    context = {
        'form': form,
        'assignment': assignment,
        'submission': submission,
        'is_update': is_update,
    }
    return render(request, 'submissions/submit_assignment.html', context)

class SubmissionListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Submission
    template_name = 'submissions/submission_list.html'
    context_object_name = 'submissions'
    paginate_by = 20
    
    def test_func(self):
        return (self.request.user.is_teacher() or 
                self.request.user.is_admin_user())
    
    def get_queryset(self):
        assignment = get_object_or_404(Assignment, pk=self.kwargs['assignment_pk'])
        return Submission.objects.filter(assignment=assignment).select_related('student')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignment'] = get_object_or_404(Assignment, pk=self.kwargs['assignment_pk'])
        return context

class SubmissionDetailView(LoginRequiredMixin, DetailView):
    model = Submission
    template_name = 'submissions/submission_detail.html'
    context_object_name = 'submission'
    
    def get_object(self):
        return get_object_or_404(
            Submission,
            pk=self.kwargs['pk'],
            assignment__pk=self.kwargs['assignment_pk']
        )

@login_required
def my_submissions(request):
    if not request.user.is_student():
        messages.error(request, 'Only students can view their submissions.')
        return redirect('courses:course_list')
    
    submissions = Submission.objects.filter(student=request.user).select_related(
        'assignment__course'
    ).order_by('-submitted_at')
    
    return render(request, 'submissions/my_submissions.html', {'submissions': submissions})