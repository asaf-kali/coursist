from django.core.management import BaseCommand
from academic_helper.management.init_data import create_all


class Command(BaseCommand):
    def handle(self, *args, **options):
        create_all()
