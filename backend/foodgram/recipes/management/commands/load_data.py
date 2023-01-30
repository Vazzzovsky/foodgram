import json
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag

class Command(BaseCommand):
    def handle(self, *args, **options) -> None:
        
        with open('data/ingredients.json', 'rb') as f:
          data = json.load(f)
          for i in data:
            ingredient = Ingredient()
            ingredient.name  = i['name']
            ingredient.measurement_unit = i['measurement_unit']
            ingredient.save()

        with open('data/tags.json', 'rb') as f:
          data = json.load(f)
          for i in data:
            tag = Tag()
            tag.name  = i['name']
            tag.color = i['color']
            tag.slug = i['slug']
            tag.save()