from django.core.management.base import BaseCommand
from core_apps.questions.models import ExamJourney

class Command(BaseCommand):
    help = 'Update all ExamJourney instances to set progress to an empty dictionary'

    def handle(self, *args, **kwargs):
        # Get all ExamJourney instances
        exam_journeys = ExamJourney.objects.all()

        # Update each instance
        for exam in exam_journeys:
            exam.progress = {}
            exam.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {exam_journeys.count()} ExamJourney instances'))