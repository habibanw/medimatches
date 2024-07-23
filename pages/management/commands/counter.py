from django.core.management.base import BaseCommand, CommandError
from pages.models import Provider

class Command(BaseCommand):
    help = 'Counts provider rows'

    def handle(self, *args, **options):
        count = Provider.objects.count()

        self.stdout.write(self.style.SUCCESS('Providers count: %d' % count))

