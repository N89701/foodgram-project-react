import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from kitchen.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка данных для модели ингредиента'

    def handle(self, *args, **options):
        with open(settings.BASE_DIR / 'data/ingredients.csv',
                  'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            ingredients = []
            for row in reader:
                ingredients.append(Ingredient(
                    name=row[0],
                    measurement_unit=row[1]
                ))
            Ingredient.objects.bulk_create(ingredients)
