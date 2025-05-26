from rest_framework import serializers
from .models import JobPosting, Resume, Evaluation

class JobPostingSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosting
        fields = '__all__'

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = '__all__'

class EvaluationSerializer(serializers.ModelSerializer):
    resume_name = serializers.CharField(source='resume.name', read_only=True)
    job_title = serializers.CharField(source='job_posting.title', read_only=True)
    
    class Meta:
        model = Evaluation
        fields = '__all__'