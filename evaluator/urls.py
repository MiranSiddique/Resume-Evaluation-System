from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobPostingViewSet, ResumeViewSet, EvaluationViewSet

router = DefaultRouter()
router.register(r'job-postings', JobPostingViewSet)
router.register(r'resumes', ResumeViewSet)
router.register(r'evaluations', EvaluationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]