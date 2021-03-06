from django.db import migrations
import json

APP_NAME = 'core'
FILE_CATEGORIES = 'core/data/categories.json'
MODEL_IMAGE_CATEGORY = 'ImageCategory'


def init(apps, schema_editor):
    data = json.load(open(FILE_CATEGORIES))
    model = apps.get_model(APP_NAME, MODEL_IMAGE_CATEGORY)

    for item in data:
        item_dict = dict(item)
        obj, _ = model.objects.get_or_create(name=item_dict['name'])
        obj.save()


def reverse(apps, schema_editor):
    data = json.load(open(FILE_CATEGORIES))
    model = apps.get_model(APP_NAME, MODEL_IMAGE_CATEGORY)

    for item in data:
        item_dict = dict(item)
        obj, _ = model.objects.get_or_create(name=item_dict['name'])
        obj.delete()


class Migration(migrations.Migration):

    dependencies = [
        (APP_NAME, '0001_initial'),
    ]

    operations = [
        migrations.RunPython(init, reverse)
    ]
