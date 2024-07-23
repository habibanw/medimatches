from django.core.management.base import BaseCommand, CommandError
from pages.models import Provider

class Command(BaseCommand):
    help = 'Delete all providers'

    def handle(self, *args, **options):
        Provider.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Providers deleted'))