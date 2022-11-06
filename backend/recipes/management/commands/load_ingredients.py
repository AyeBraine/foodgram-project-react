# isort: skip_file
import json

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient

DIR = settings.BASE_DIR


class Command(BaseCommand):
    help = 'Loads ingredients data to database from json files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Path to json file'
        )

    def handle(self, *args, **options):
        with open(options['file'], 'r', encoding="utf-8-sig") as file:
            data = json.load(file)
            for row in data:
                Ingredient.objects.get_or_create(**row)

        # for csv_name in CSV_MODEL:
        #     with open(
        #         DIR + f'/static/data/{csv_name}.csv',
        #         'r',
        #         encoding="utf-8-sig"
        #     ) as file:
        #         reader = csv.DictReader(file, delimiter=",")
        #         for row in reader:
        #             CSV_MODEL[csv_name].objects.get_or_create(**row)
