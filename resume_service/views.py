from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import fitz  # PyMuPDF
import os
import sys
import json

# Add the MLModel directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'MLModel'))

from .models import Resume
from .forms import ResumeUploadForm

@login_required
def upload_resume(request):
    """Handle resume upload and text extraction"""
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            
            # Extract text from PDF
            try:
                pdf_file = request.FILES['file']
                doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
                text = "\n".join([page.get_text("text") for page in doc])
                resume.extracted_text = text.strip()
                resume.save()
                
                messages.success(request, 'Resume uploaded successfully!')
                return redirect('resume_list')
            except Exception as e:
                messages.error(request, f'Error processing PDF: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ResumeUploadForm()
    
    return render(request, 'resume_service/upload_resume.html', {'form': form})

@login_required
def resume_list(request):
    """Display user's uploaded resumes"""
    resumes = Resume.objects.filter(user=request.user, is_active=True)
    return render(request, 'resume_service/resume_list.html', {'resumes': resumes})

@login_required
def delete_resume(request, resume_id):
    """Delete a resume"""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    if request.method == 'POST':
        resume.is_active = False
        resume.save()
        messages.success(request, 'Resume deleted successfully!')
        return redirect('resume_list')
    
    return render(request, 'resume_service/delete_resume.html', {'resume': resume})

@login_required
def get_recommendations(request, resume_id):
    """Get job recommendations for a specific resume"""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    if not resume.extracted_text:
        messages.error(request, 'No text extracted from resume. Please re-upload.')
        return redirect('resume_list')
    
    try:
        # Import the ML model
        from model import JobRecommendationSystem
        
        # Initialize the recommendation system
        jobs_csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'MLModel', 'JobsFE.csv')
        recommender = JobRecommendationSystem(jobs_csv_path)
        
        # Get recommendations
        recommendations = recommender.recommend_jobs(resume.extracted_text, top_n=20)
        recommended_jobs = recommendations["recommended_jobs"]
        
        return render(request, 'resume_service/recommendations.html', {
            'resume': resume,
            'recommendations': recommended_jobs
        })
        
    except Exception as e:
        messages.error(request, f'Error getting recommendations: {str(e)}')
        return redirect('resume_list')

@csrf_exempt
@require_http_methods(["POST"])
def api_get_recommendations(request):
    """API endpoint for getting job recommendations"""
    try:
        data = json.loads(request.body)
        resume_text = data.get('resume_text', '')
        
        if not resume_text:
            return JsonResponse({'error': 'Resume text is required'}, status=400)
        
        # Import the ML model
        from model import JobRecommendationSystem
        
        # Initialize the recommendation system
        jobs_csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'MLModel', 'JobsFE.csv')
        recommender = JobRecommendationSystem(jobs_csv_path)
        
        # Get recommendations
        recommendations = recommender.recommend_jobs(resume_text, top_n=20)
        
        return JsonResponse(recommendations)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
