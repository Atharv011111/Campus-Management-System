from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegistrationForm, UserProfileForm
from .models import User

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

class CustomLogoutView(LogoutView):
    next_page = 'home'

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}

    # First: Check if superuser
    if user.is_superuser:
        from courses.models import Course, Enrollment
        from submissions.models import Submission
        context.update({
            'total_courses': Course.objects.count(),
            'total_enrollments': Enrollment.objects.count(),
            'total_submissions': Submission.objects.count(),
        })
        return render(request, 'accounts/admin_dashboard.html', context)

    # Then check other roles
    if user.is_student():
        from courses.models import Enrollment
        enrollments = Enrollment.objects.filter(student=user).select_related('course')
        context['enrollments'] = enrollments
        return render(request, 'accounts/student_dashboard.html', context)

    elif user.is_teacher():
        from courses.models import Course
        courses = Course.objects.filter(teacher=user)
        context['courses'] = courses
        return render(request, 'accounts/teacher_dashboard.html', context)

    # Fallback — just in case
    return render(request, 'accounts/unknown_role.html', context)

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile.html'
    success_url = '/accounts/dashboard/'
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)