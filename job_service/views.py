from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import logging
import json

from .models import Job, JobDescription
from .forms import JobDescriptionForm

# Import advanced ML system
from ml_service.models import AdvancedJobRecommendationSystem

logger = logging.getLogger(__name__)

def homepage(request):
    """Main homepage with two sections: Post a Job and Find a Job"""
    return render(request, 'job_service/homepage.html')

def post_job(request):
    """Handle job posting by employers"""
    if request.method == 'POST':
        form = JobDescriptionForm(request.POST, request.FILES)
        if form.is_valid():
            job_desc = form.save()
            messages.success(request, 'Job posted successfully! Your job is now live and candidates can apply.')
            return redirect('job_service:job_description_detail', job_id=job_desc.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = JobDescriptionForm()
    
    return render(request, 'job_service/post_job.html', {'form': form})

def upload_job_description(request):
    """Handle job description upload by employers"""
    if request.method == 'POST':
        form = JobDescriptionForm(request.POST, request.FILES)
        if form.is_valid():
            job_desc = form.save()
            messages.success(request, 'Job description uploaded successfully!')
            return redirect('job_service:job_description_detail', job_id=job_desc.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = JobDescriptionForm()
    
    return render(request, 'job_service/upload_job_description.html', {'form': form})

def job_description_detail(request, job_id):
    """Show job description details and potential candidates"""
    job_desc = get_object_or_404(JobDescription, id=job_id)
    
    # Get candidate recommendations for this job
    candidates = get_candidate_recommendations(job_desc)
    
    return render(request, 'job_service/job_description_detail.html', {
        'job_description': job_desc,
        'candidates': candidates
    })

def get_candidate_recommendations(job_description, top_n=20):
    """Get candidate recommendations for a job description"""
    try:
        from resume_service.models import Resume
        
        # Get all resumes from database
        resumes = Resume.objects.filter(user__isnull=True)  # Anonymous resumes
        
        if resumes.count() == 0:
            return []
        
        # Initialize ML system with resumes
        ml_system = AdvancedJobRecommendationSystem(resumes)
        
        # Get job text for matching
        job_text = job_description.job_text
        
        # Get candidate recommendations using hybrid method
        candidates = ml_system.get_hybrid_recommendations(job_text, top_n)
        
        logger.info(f"Found {len(candidates)} candidate recommendations for job: {job_description.position}")
        return candidates
        
    except Exception as e:
        logger.error(f"Error getting candidate recommendations: {str(e)}")
        return []

def job_list(request):
    """List all job descriptions"""
    job_descriptions = JobDescription.objects.filter(is_active=True).order_by('-created_at')
    
    return render(request, 'job_service/job_list.html', {
        'job_descriptions': job_descriptions
    })

@csrf_exempt
@require_http_methods(["POST"])
def api_get_candidates(request):
    """API endpoint for getting candidate recommendations for a job"""
    try:
        data = json.loads(request.body)
        job_text = data.get('job_text', '')
        
        if not job_text:
            return JsonResponse({'error': 'Job text is required'}, status=400)
        
        # Get candidate recommendations
        candidates = get_candidate_recommendations_from_text(job_text)
        
        return JsonResponse({'candidates': candidates})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_candidate_recommendations_from_text(job_text, top_n=20):
    """Get candidate recommendations from job text"""
    try:
        from resume_service.models import Resume
        
        resumes = Resume.objects.filter(user__isnull=True)
        
        if resumes.count() == 0:
            return []
        
        # Initialize ML system
        ml_system = AdvancedJobRecommendationSystem(resumes)
        
        # Get recommendations
        candidates = ml_system.get_hybrid_recommendations(job_text, top_n)
        
        return candidates
        
    except Exception as e:
        logger.error(f"Error getting candidate recommendations from text: {str(e)}")
        return []
