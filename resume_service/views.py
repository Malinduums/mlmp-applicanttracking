from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import fitz  # PyMuPDF
import os
import json
import logging
import re

# Set up logging
logger = logging.getLogger(__name__)

from .models import Resume
from .forms import ResumeUploadForm

# Import advanced ML system
from ml_service.models import AdvancedJobRecommendationSystem

def upload_resume(request):
    """Handle resume upload and text extraction - No login required"""
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            # Set a default user or leave user as None for anonymous uploads
            resume.user = None
            
            # Extract text from PDF
            try:
                pdf_file = request.FILES['file']
                doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
                text = "\n".join([page.get_text("text") for page in doc])
                resume.extracted_text = text.strip()
                resume.save()
                
                messages.success(request, 'Resume uploaded successfully!')
                return redirect('resume_service:get_recommendations', resume_id=resume.id)
            except Exception as e:
                logger.error(f"Error processing PDF: {str(e)}")
                messages.error(request, f'Error processing PDF: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ResumeUploadForm()
    
    return render(request, 'resume_service/upload_resume.html', {'form': form})

def extract_skills_from_resume(resume_text):
    """Extract skills from resume text using pattern matching"""
    skills = []
    
    # Common technical skills
    technical_skills = [
        'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js', 'express',
        'sql', 'mysql', 'postgresql', 'mongodb', 'aws', 'azure', 'docker', 'kubernetes',
        'git', 'github', 'html', 'css', 'bootstrap', 'jquery', 'php', 'c#', 'c++',
        'machine learning', 'ai', 'artificial intelligence', 'data science', 'analytics',
        'excel', 'powerbi', 'tableau', 'r', 'matlab', 'tensorflow', 'pytorch',
        'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'jupyter'
    ]
    
    # Common soft skills
    soft_skills = [
        'leadership', 'communication', 'teamwork', 'problem solving', 'project management',
        'agile', 'scrum', 'kanban', 'customer service', 'sales', 'marketing',
        'research', 'analysis', 'planning', 'organization', 'time management'
    ]
    
    resume_lower = resume_text.lower()
    
    # Extract technical skills
    for skill in technical_skills:
        if skill in resume_lower:
            skills.append(skill)
    
    # Extract soft skills
    for skill in soft_skills:
        if skill in resume_lower:
            skills.append(skill)
    
    return skills

def get_advanced_recommendations(resume_text, method='hybrid'):
    """Get advanced ML-powered job recommendations"""
    try:
        # Import Job model from job_service
        from job_service.models import Job
        
        # Get all active jobs from database
        jobs = Job.objects.filter(is_active=True)
        
        if jobs.count() == 0:
            logger.warning("No jobs found in database")
            return []
        
        # Initialize advanced ML system
        ml_system = AdvancedJobRecommendationSystem(jobs)
        
        # Get recommendations based on method
        if method == 'tfidf':
            recommendations = ml_system.get_tfidf_recommendations(resume_text)
        elif method == 'semantic':
            recommendations = ml_system.get_semantic_recommendations(resume_text)
        else:  # hybrid
            recommendations = ml_system.get_hybrid_recommendations(resume_text)
        
        logger.info(f"Advanced ML recommendations: {len(recommendations)} jobs using {method} method")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error in advanced recommendations: {str(e)}")
        # Fallback to simple method
        return get_simple_recommendations(resume_text)

def get_simple_recommendations(resume_text):
    """Fallback to simple keyword-based recommendations"""
    try:
        from job_service.models import Job
        
        jobs = Job.objects.filter(is_active=True)
        if jobs.count() == 0:
            return []
        
        resume_skills = extract_skills_from_resume(resume_text)
        job_similarities = []
        
        for job in jobs:
            job_dict = {
                'position': job.position,
                'workplace': job.workplace,
                'working_mode': job.working_mode,
                'job_role_and_duties': job.job_role_and_duties,
                'requisite_skill': job.requisite_skill,
                'salary_min': float(job.salary_min) if job.salary_min else None,
                'salary_max': float(job.salary_max) if job.salary_max else None,
                'location': job.location,
                'created_at': job.created_at,
            }
            
            # Simple skill matching
            job_text = f"{job_dict.get('position', '')} {job_dict.get('job_role_and_duties', '')} {job_dict.get('requisite_skill', '')}".lower()
            skill_matches = sum(1 for skill in resume_skills if skill in job_text)
            
            if len(resume_skills) > 0:
                similarity_score = min(95, (skill_matches / len(resume_skills)) * 100 + 20)
            else:
                similarity_score = 50
            
            job_dict['similarity_score'] = round(similarity_score, 1)
            job_dict['skill_matches'] = skill_matches
            job_dict['ai_ranked'] = True
            job_dict['method'] = 'Simple Keyword Matching'
            job_similarities.append(job_dict)
        
        # Sort by similarity score
        job_similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        return job_similarities[:20]
        
    except Exception as e:
        logger.error(f"Error in simple recommendations: {str(e)}")
        return []

def get_recommendations(request, resume_id):
    """Get advanced AI-powered job recommendations based on CV content"""
    resume = get_object_or_404(Resume, id=resume_id, user__isnull=True)
    
    if not resume.extracted_text:
        messages.error(request, 'No text extracted from resume. Please re-upload.')
        return redirect('resume_service:upload_resume')
    
    try:
        # Get ML method from request (default to hybrid)
        ml_method = request.GET.get('method', 'hybrid')
        
        # Get advanced recommendations
        recommended_jobs = get_advanced_recommendations(resume.extracted_text, ml_method)
        
        if not recommended_jobs:
            messages.warning(request, 'No recommendations found. Using fallback method.')
            recommended_jobs = get_simple_recommendations(resume.extracted_text)
        
        # Extract skills for display
        resume_skills = extract_skills_from_resume(resume.extracted_text)
        
        # Delete the resume after processing
        resume.delete()
        
        return render(request, 'resume_service/recommendations.html', {
            'resume': resume,
            'recommendations': recommended_jobs,
            'ai_powered': True,
            'total_jobs_analyzed': len(recommended_jobs),
            'resume_skills': resume_skills,
            'ml_method': ml_method
        })
        
    except Exception as e:
        logger.error(f"Error in recommendations: {str(e)}")
        messages.error(request, f'Error processing recommendations: {str(e)}')
        return redirect('resume_service:upload_resume')

@csrf_exempt
@require_http_methods(["POST"])
def api_get_recommendations(request):
    """API endpoint for getting advanced AI-powered job recommendations"""
    try:
        data = json.loads(request.body)
        resume_text = data.get('resume_text', '')
        ml_method = data.get('method', 'hybrid')
        
        if not resume_text:
            return JsonResponse({'error': 'Resume text is required'}, status=400)
        
        # Get advanced recommendations
        recommended_jobs = get_advanced_recommendations(resume_text, ml_method)
        
        if not recommended_jobs:
            recommended_jobs = get_simple_recommendations(resume_text)
        
        return JsonResponse({'recommended_jobs': recommended_jobs})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
