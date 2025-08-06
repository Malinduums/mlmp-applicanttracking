from django.db import models

# Create your models here.

class Job(models.Model):
    WORKING_MODE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    ]
    
    position = models.CharField(max_length=255)
    workplace = models.CharField(max_length=255)
    working_mode = models.CharField(max_length=20, choices=WORKING_MODE_CHOICES)
    job_role_and_duties = models.TextField()
    requisite_skill = models.TextField()
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.position} at {self.workplace}"
    
    @property
    def job_text(self):
        """Combine job fields for ML processing"""
        return f"{self.workplace} {self.working_mode} {self.position} {self.job_role_and_duties} {self.requisite_skill}"

class JobDescription(models.Model):
    """Model for employers to upload job descriptions"""
    WORKING_MODE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    ]
    
    # Employer information
    employer_name = models.CharField(max_length=255)
    employer_email = models.EmailField()
    contact_person = models.CharField(max_length=255)
    
    # Job details
    position = models.CharField(max_length=255)
    workplace = models.CharField(max_length=255)
    working_mode = models.CharField(max_length=20, choices=WORKING_MODE_CHOICES)
    job_role_and_duties = models.TextField()
    requisite_skill = models.TextField()
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    
    # Additional fields
    job_description_file = models.FileField(upload_to='job_descriptions/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.position} at {self.workplace} by {self.employer_name}"
    
    @property
    def job_text(self):
        """Combine job fields for ML processing"""
        return f"{self.workplace} {self.working_mode} {self.position} {self.job_role_and_duties} {self.requisite_skill}"
