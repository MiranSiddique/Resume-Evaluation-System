from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import JobPosting, Resume, Evaluation
from .serializers import JobPostingSerializer, ResumeSerializer, EvaluationSerializer
from .utils.pdf_extractor import ResumeExtractor
from .utils.evaluator import ResumeEvaluator
import json

class JobPostingViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer

class ResumeViewSet(viewsets.ModelViewSet):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        resume = serializer.save()
        
        # Extract data from PDF
        extractor = ResumeExtractor()
        try:
            extracted_data = extractor.extract_all_data(resume.file)
            
            # Update resume with extracted data
            for field, value in extracted_data.items():
                setattr(resume, field, value)
            resume.save()
            
            return Response(ResumeSerializer(resume).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            resume.delete()  # Clean up if extraction fails
            return Response({'error': f'Failed to extract resume data: {str(e)}'}, 
                          status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'])
    def update_extracted_data(self, request, pk=None):
        resume = self.get_object()
        
        # Update only the fields that are provided
        allowed_fields = ['name', 'email', 'phone', 'education', 'experience', 'skills']
        for field in allowed_fields:
            if field in request.data:
                setattr(resume, field, request.data[field])
        
        resume.save()
        return Response(ResumeSerializer(resume).data)

class EvaluationViewSet(viewsets.ModelViewSet):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    
    @action(detail=False, methods=['post'])
    def analyze(self, request):
        resume_id = request.data.get('resume_id')
        job_posting_id = request.data.get('job_posting_id')
        
        if not resume_id or not job_posting_id:
            return Response({'error': 'resume_id and job_posting_id are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        resume = get_object_or_404(Resume, id=resume_id)
        job_posting = get_object_or_404(JobPosting, id=job_posting_id)
        
        # Check if evaluation already exists
        existing_evaluation = Evaluation.objects.filter(
            resume=resume, job_posting=job_posting
        ).first()
        
        if existing_evaluation:
            return Response(EvaluationSerializer(existing_evaluation).data)
        
        # Perform evaluation
        evaluator = ResumeEvaluator()
        evaluation_data = evaluator.evaluate_resume(resume, job_posting)
        
        # Create evaluation record
        evaluation = Evaluation.objects.create(
            resume=resume,
            job_posting=job_posting,
            **evaluation_data
        )
        
        return Response(EvaluationSerializer(evaluation).data)
