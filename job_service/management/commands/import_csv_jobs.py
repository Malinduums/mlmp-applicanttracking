from django.core.management.base import BaseCommand
from job_service.models import Job
import pandas as pd
import os
import sys

class Command(BaseCommand):
    help = 'Import first 500 jobs from CSV file to PostgreSQL database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-file',
            type=str,
            default='MLModel/JobsFE.csv',
            help='Path to the CSV file (default: MLModel/JobsFE.csv)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=500,
            help='Number of jobs to import (default: 500)'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        limit = options['limit']
        
        # Check if CSV file exists
        if not os.path.exists(csv_file):
            self.stdout.write(
                self.style.ERROR(f'CSV file not found: {csv_file}')
            )
            return
        
        try:
            # Read CSV file
            self.stdout.write(f'Reading CSV file: {csv_file}')
            df = pd.read_csv(csv_file)
            
            # Limit to first N jobs
            df = df.head(limit)
            self.stdout.write(f'Found {len(df)} jobs to import')
            
            # Clear existing jobs (optional)
            self.stdout.write('Clearing existing jobs...')
            Job.objects.all().delete()
            
            # Import jobs
            created_count = 0
            for index, row in df.iterrows():
                try:
                    # Map CSV columns to Job model fields
                    job_data = {
                        'position': str(row.get('position', 'Unknown Position'))[:255],
                        'workplace': str(row.get('workplace', 'Unknown Company'))[:255],
                        'working_mode': self.map_working_mode(row.get('working_mode', 'full_time')),
                        'job_role_and_duties': str(row.get('job_role_and_duties', ''))[:10000],
                        'requisite_skill': str(row.get('requisite_skill', ''))[:10000],
                        'salary_min': self.parse_salary(row.get('salary_min')),
                        'salary_max': self.parse_salary(row.get('salary_max')),
                        'location': str(row.get('location', ''))[:255],
                        'is_active': True
                    }
                    
                    # Create job
                    job = Job.objects.create(**job_data)
                    created_count += 1
                    
                    if created_count % 50 == 0:
                        self.stdout.write(f'Imported {created_count} jobs...')
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Error importing job {index}: {str(e)}')
                    )
                    continue
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported {created_count} jobs to PostgreSQL')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading CSV file: {str(e)}')
            )
    
    def map_working_mode(self, mode):
        """Map working mode to Django choices"""
        mode = str(mode).lower().strip()
        
        # Map common variations to Django choices
        mode_mapping = {
            'full time': 'full_time',
            'full-time': 'full_time',
            'part time': 'part_time',
            'part-time': 'part_time',
            'contract': 'contract',
            'freelance': 'freelance',
            'internship': 'internship',
            'remote': 'remote',
            'work from home': 'remote',
            'wfh': 'remote'
        }
        
        return mode_mapping.get(mode, 'full_time')
    
    def parse_salary(self, salary):
        """Parse salary field to decimal"""
        if pd.isna(salary) or salary == '' or salary is None:
            return None
        
        try:
            # Remove currency symbols and commas
            salary_str = str(salary).replace('$', '').replace(',', '').replace('USD', '').strip()
            return float(salary_str)
        except (ValueError, TypeError):
            return None 