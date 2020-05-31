from django.core.management import BaseCommand

from academic_helper.logic.shnaton_parser import ShnatonParser


# TODO: Add arguments: course number
class Command(BaseCommand):
    def handle(self, *args, **options):
        ShnatonParser.fetch_course(1530)
