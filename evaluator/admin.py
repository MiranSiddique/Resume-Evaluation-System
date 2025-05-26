from django.contrib import admin
from .models import JobPosting, Resume, Evaluation

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'location', 'experience_required', 'created_at']
    search_fields = ['title', 'department', 'location']

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'uploaded_at']
    search_fields = ['name', 'email']

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['resume', 'job_posting', 'final_score', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['resume__name', 'job_posting__title']