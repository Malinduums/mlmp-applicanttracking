from django.core.management.base import BaseCommand
from job_service.models import Job

class Command(BaseCommand):
    help = 'Clear all jobs from the database'

    def handle(self, *args, **options):
        # Delete all jobs
        deleted_count = Job.objects.all().count()
        Job.objects.all().delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {deleted_count} jobs from the database')
        ) 