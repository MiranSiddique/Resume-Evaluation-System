from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import json

class JobPosting(models.Model):
    title = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField()
    required_skills = models.TextField(help_text="Comma-separated skills")
    experience_required = models.IntegerField(validators=[MinValueValidator(0)])
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    @property
    def skills_list(self):
        return [skill.strip() for skill in self.required_skills.split(',')]

class Resume(models.Model):
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Extracted data fields
    name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    education = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    
    # Raw extracted text
    raw_text = models.TextField(blank=True)
    
    def __str__(self):
        return f"Resume {self.id} - {self.name or 'Unknown'}"
    
    @property
    def skills_list(self):
        if self.skills:
            return [skill.strip() for skill in self.skills.split(',')]
        return []

class Evaluation(models.Model):
    SCORE_CATEGORIES = [
        ('excellent', 'Excellent (80-100)'),
        ('good', 'Good (60-79)'),
        ('average', 'Average (40-59)'),
        ('below_average', 'Below Average (0-39)'),
    ]
    
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    
    # Rule-based scores
    skill_match_score = models.FloatField(default=0)
    experience_score = models.FloatField(default=0)
    education_score = models.FloatField(default=0)
    
    # Cosine similarity score
    cosine_similarity_score = models.FloatField(default=0)
    
    # Final weighted score
    final_score = models.FloatField(default=0)
    category = models.CharField(max_length=20, choices=SCORE_CATEGORIES)
    
    # Additional analysis data
    matched_skills = models.TextField(blank=True)  # JSON
    missing_skills = models.TextField(blank=True)  # JSON
    keyword_highlights = models.TextField(blank=True)  # JSON
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Evaluation for {self.resume.name} - {self.final_score:.2f}"
    
    def get_category_from_score(self, score):
        if score >= 80:
            return 'excellent'
        elif score >= 60:
            return 'good'
        elif score >= 40:
            return 'average'
        else:
            return 'below_average'