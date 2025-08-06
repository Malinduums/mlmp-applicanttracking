from django.urls import path
from . import views

app_name = 'resume_service'

urlpatterns = [
    path('upload/', views.upload_resume, name='upload_resume'),
    path('recommendations/<int:resume_id>/', views.get_recommendations, name='get_recommendations'),
    path('api/recommendations/', views.api_get_recommendations, name='api_recommendations'),
] 