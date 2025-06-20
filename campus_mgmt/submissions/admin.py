from django.contrib import admin
from .models import Submission

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'submitted_at', 'updated_at', 'filename')
    list_filter = ('submitted_at', 'assignment__course', 'assignment')
    search_fields = ('student__username', 'assignment__title')
    date_hierarchy = 'submitted_at'
    readonly_fields = ('submitted_at', 'updated_at')
    
    def filename(self, obj):
        return obj.filename()
    filename.short_description = 'File Name'