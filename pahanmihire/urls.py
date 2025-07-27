"""
URL configuration for pahanmihire project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from user_service import views as user_views

urlpatterns = [
    # Django's default admin (optional – for developers only)
    
    path('admin/', admin.site.urls),

    # Custom admin dashboard
    path('admin-panel/', include('adminpanel.urls')), 
    
   
    path('', user_views.index, name='index'),
    # API Microservices
     path('api/user/', include('user_service.urls')),
    path('api/resume/', include('resume_service.urls')),
    # path('api/job/', include('job_service.urls')),
    # path('api/application/', include('application_service.urls')),
    # path('api/interview/', include('interview_service.urls')),
    # path('api/ai/', include('ai_service.urls')),
    # path('api/xai/', include('xai_service.urls')),
    # path('api/notify/', include('notification_service.urls')),
    # path('api/recommend/', include('recommendation_service.urls')),
    # path('api/analytics/', include('analytics_service.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


