from django.urls import path
from . import views

app_name = 'job_service'

urlpatterns = [
    path('jobs/', views.job_list, name='job_list'),
    path('upload-job/', views.upload_job_description, name='upload_job_description'),
    path('job/<int:job_id>/', views.job_description_detail, name='job_description_detail'),
    path('api/candidates/', views.api_get_candidates, name='api_get_candidates'),
] 