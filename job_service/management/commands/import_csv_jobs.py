import csv
import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from job_service.models import Job


class Command(BaseCommand):
    help = 'Import jobs from JobsFE.csv file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='JobsFE.csv',
            help='Path to the CSV file (default: JobsFE.csv)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing jobs before importing'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        clear_existing = options['clear']

        # Check if file exists
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f'File {file_path} not found!')
            )
            return

        # Clear existing jobs if requested
        if clear_existing:
            Job.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS('Cleared existing jobs.')
            )

        # Import jobs
        imported_count = 0
        skipped_count = 0
        error_count = 0

        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    try:
                        # Clean and validate data
                        job_id = row.get('Job Id', '').strip()
                        workplace = row.get('workplace', '').strip()
                        working_mode = row.get('working_mode', '').strip().lower()
                        salary = row.get('salary', '').strip()
                        position = row.get('position', '').strip()
                        job_role_and_duties = row.get('job_role_and_duties', '').strip()
                        requisite_skill = row.get('requisite_skill', '').strip()
                        offer_details = row.get('offer_details', '').strip()

                        # Skip if essential fields are empty
                        if not position or not workplace:
                            skipped_count += 1
                            continue

                        # Map working mode to choices
                        working_mode_mapping = {
                            'full time': 'full_time',
                            'part time': 'part_time',
                            'contract': 'contract',
                            'freelance': 'freelance',
                            'internship': 'internship',
                            'remote': 'remote',
                        }
                        
                        working_mode = working_mode_mapping.get(working_mode, 'full_time')

                        # Parse salary
                        salary_min = None
                        salary_max = None
                        if salary:
                            try:
                                # Remove currency symbols and commas
                                salary_clean = salary.replace('$', '').replace(',', '').replace('£', '').replace('€', '')
                                if '-' in salary_clean:
                                    parts = salary_clean.split('-')
                                    if len(parts) == 2:
                                        salary_min = Decimal(parts[0].strip())
                                        salary_max = Decimal(parts[1].strip())
                                else:
                                    salary_min = Decimal(salary_clean)
                                    salary_max = salary_min
                            except (ValueError, TypeError):
                                pass

                        # Create job object
                        job = Job(
                            position=position,
                            workplace=workplace,
                            working_mode=working_mode,
                            job_role_and_duties=job_role_and_duties,
                            requisite_skill=requisite_skill,
                            salary_min=salary_min,
                            salary_max=salary_max,
                            location=workplace,  # Use workplace as location
                        )
                        
                        job.save()
                        imported_count += 1

                        # Progress indicator
                        if imported_count % 100 == 0:
                            self.stdout.write(f'Imported {imported_count} jobs...')

                    except Exception as e:
                        error_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'Error importing row: {e}')
                        )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Import completed! Imported: {imported_count}, Skipped: {skipped_count}, Errors: {error_count}'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading CSV file: {e}')
            ) 