from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Course, Assignment, Enrollment, Result
from .forms import CourseForm, AssignmentForm, EnrollmentForm, ResultForm

# Course Views
class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Course.objects.select_related('teacher')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        return queryset

class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user
        
        if user.is_student():
            context['is_enrolled'] = Enrollment.objects.filter(
                student=user, course=course, is_active=True
            ).exists()
        
        context['assignments'] = course.assignments.all()
        return context

class CourseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('courses:course_list')
    
    def test_func(self):
        return self.request.user.is_teacher() or self.request.user.is_admin_user()
    
    def form_valid(self, form):
        form.instance.teacher = self.request.user
        messages.success(self.request, 'Course created successfully!')
        return super().form_valid(form)

class CourseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('courses:course_list')
    
    def test_func(self):
        course = self.get_object()
        return (course.teacher == self.request.user or 
                self.request.user.is_admin_user())
    
    def form_valid(self, form):
        messages.success(self.request, 'Course updated successfully!')
        return super().form_valid(form)

# Enrollment Views
@login_required
def enroll_course(request, pk):
    if not request.user.is_student():
        messages.error(request, 'Only students can enroll in courses.')
        return redirect('courses:course_list')
    
    course = get_object_or_404(Course, pk=pk)
    
    if course.is_full():
        messages.error(request, 'Course is full.')
        return redirect('courses:course_detail', pk=pk)
    
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={'is_active': True}
    )
    
    if created:
        messages.success(request, f'Successfully enrolled in {course.title}!')
    else:
        if enrollment.is_active:
            messages.warning(request, 'You are already enrolled in this course.')
        else:
            enrollment.is_active = True
            enrollment.save()
            messages.success(request, f'Re-enrolled in {course.title}!')
    
    return redirect('courses:course_detail', pk=pk)

@login_required
def withdraw_course(request, pk):
    if not request.user.is_student():
        messages.error(request, 'Only students can withdraw from courses.')
        return redirect('courses:course_list')
    
    course = get_object_or_404(Course, pk=pk)
    
    try:
        enrollment = Enrollment.objects.get(
            student=request.user,
            course=course,
            is_active=True
        )
        enrollment.is_active = False
        enrollment.save()
        messages.success(request, f'Successfully withdrawn from {course.title}.')
    except Enrollment.DoesNotExist:
        messages.error(request, 'You are not enrolled in this course.')
    
    return redirect('courses:course_detail', pk=pk)

# Assignment Views
class AssignmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'courses/assignment_form.html'
    
    def test_func(self):
        course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        return (course.teacher == self.request.user or 
                self.request.user.is_admin_user())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        context['course'] = course
        return context

    def form_valid(self, form):
        course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        form.instance.course = course
        messages.success(self.request, 'Assignment created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('courses:course_detail', kwargs={'pk': self.kwargs['course_pk']})


class AssignmentDetailView(LoginRequiredMixin, DetailView):
    model = Assignment
    template_name = 'courses/assignment_detail.html'
    context_object_name = 'assignment'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assignment = self.object
        user = self.request.user
        
        if user.is_student():
            try:
                submission = assignment.submissions.get(student=user)
                context['submission'] = submission
            except:
                context['submission'] = None
        
        return context

# Result Views
@login_required
def grade_assignment(request, assignment_pk, student_pk):
    assignment = get_object_or_404(Assignment, pk=assignment_pk)
    student = get_object_or_404(
        assignment.course.enrollments.filter(is_active=True),
        student__pk=student_pk
    ).student  # Accessing the Student object directly
    
    if not (assignment.course.teacher == request.user or request.user.is_admin_user()):
        messages.error(request, 'Permission denied.')
        return redirect('courses:course_list')
    
    try:
        result = Result.objects.get(student=student, assignment=assignment)
    except Result.DoesNotExist:
        result = None
    
    if request.method == 'POST':
        form = ResultForm(request.POST, instance=result, assignment=assignment)
        if form.is_valid():
            result = form.save(commit=False)
            result.student = student
            result.assignment = assignment
            result.save()
            messages.success(request, 'Grade saved successfully!')
            return redirect('courses:course_detail', pk=assignment.course.pk)
    else:
        form = ResultForm(instance=result, assignment=assignment)
    
    context = {
        'form': form,
        'assignment': assignment,
        'student': student,
        'result': result,
    }
    return render(request, 'courses/grade_form.html', context)


@login_required
def my_results(request):
    if not request.user.is_student():
        messages.error(request, 'Only students can view results.')
        return redirect('courses:course_list')
    
    results = Result.objects.filter(student=request.user).select_related(
        'assignment__course'
    ).order_by('-graded_at')
    
    return render(request, 'courses/my_results.html', {'results': results})