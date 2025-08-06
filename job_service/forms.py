from django import forms
from .models import JobDescription

class JobDescriptionForm(forms.ModelForm):
    """Form for employers to upload job descriptions"""
    
    class Meta:
        model = JobDescription
        fields = [
            'employer_name', 'employer_email', 'contact_person',
            'position', 'workplace', 'working_mode',
            'job_role_and_duties', 'requisite_skill',
            'salary_min', 'salary_max', 'location',
            'job_description_file'
        ]
        widgets = {
            'employer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Company Name'
            }),
            'employer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@company.com'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact Person Name'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Senior Python Developer'
            }),
            'workplace': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company Name'
            }),
            'working_mode': forms.Select(attrs={
                'class': 'form-control'
            }),
            'job_role_and_duties': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe the job role, responsibilities, and duties...'
            }),
            'requisite_skill': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Required skills, experience, and qualifications...'
            }),
            'salary_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Minimum salary (optional)'
            }),
            'salary_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Maximum salary (optional)'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Job location (e.g., New York, NY)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['job_description_file'].widget.attrs.update({
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx,.txt'
        })
    
    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')
        
        # Validate salary range
        if salary_min and salary_max and salary_min > salary_max:
            raise forms.ValidationError("Minimum salary cannot be greater than maximum salary.")
        
        return cleaned_data 