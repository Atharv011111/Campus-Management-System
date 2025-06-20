from django.contrib import admin
from .models import Course, Enrollment, Assignment, Result

class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    fields = ('student', 'enrolled_at', 'is_active')
    readonly_fields = ('enrolled_at',)

class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 0
    fields = ('title', 'due_date', 'max_marks')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'credits', 'start_date', 'end_date', 'enrolled_count')
    list_filter = ('credits', 'start_date', 'teacher')
    search_fields = ('title', 'description', 'teacher__username')
    date_hierarchy = 'start_date'
    inlines = [EnrollmentInline, AssignmentInline]
    
    def enrolled_count(self, obj):
        return obj.enrolled_count()
    enrolled_count.short_description = 'Enrolled Students'

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at', 'is_active')
    list_filter = ('is_active', 'enrolled_at', 'course')
    search_fields = ('student__username', 'course__title')
    date_hierarchy = 'enrolled_at'

class ResultInline(admin.TabularInline):
    model = Result
    extra = 0
    fields = ('student', 'marks_obtained', 'grade', 'graded_at')
    readonly_fields = ('graded_at',)

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date', 'max_marks', 'created_at')
    list_filter = ('due_date', 'course', 'max_marks')
    search_fields = ('title', 'description', 'course__title')
    date_hierarchy = 'due_date'
    inlines = [ResultInline]

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'marks_obtained', 'grade', 'graded_at')
    list_filter = ('grade', 'graded_at', 'assignment__course')
    search_fields = ('student__username', 'assignment__title')
    date_hierarchy = 'graded_at'