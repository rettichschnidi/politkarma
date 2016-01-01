from xml.etree import ElementTree
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from politkarma import settings
import requests

from apps.curia_vista.models import *


class Command(BaseCommand):
    help = 'Import cantons from parlament.ch'

    @transaction.atomic
    def update(self, resource_url, lang, is_main):
        from django.utils import translation
        translation.activate(lang)
        url = resource_url + '?format=xml&lang=' + lang

        self.stdout.write("Importing {}".format(url))

        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla'})
        except Exception as e:
            raise CommandError("Could not fetch file from {}".format(url))

        cantons = ElementTree.fromstring(response.content)

        if not cantons:
            raise CommandError("Not a valid XML file: {}".format(url))

        for canton in cantons:
            canton_id = canton.find('id').text
            canton_updated = canton.find('updated').text
            canton_abbreviation = canton.find('abbreviation').text
            canton_code = canton.find('code').text
            canton_name = canton.find('name').text
            if canton.find('hasMorePages') is not None:
                assert 'false' == canton.find('hasMorePages').text
            if is_main:
                canton_model, created = Canton.objects.update_or_create(id=canton_id,
                                                                        defaults={'updated': canton_updated,
                                                                                  'name': canton_name,
                                                                                  'abbreviation': canton_abbreviation,
                                                                                  'code': canton_code})
            else:
                canton_model, created = Canton.objects.update_or_create(id=canton_id,
                                                                        updated=canton_updated,
                                                                        code=canton_code,
                                                                        abbreviation=canton_abbreviation,
                                                                        defaults={
                                                                            'name': canton_name
                                                                        })
            canton_model.full_clean()
            canton_model.save()
            print(canton_model)

    def handle(self, *args, **options):
        is_main = True
        resource_url = 'http://ws.parlament.ch/Cantons'
        for lang in [x[0] for x in settings.LANGUAGES]:
            self.update(resource_url, lang, is_main)
            is_main = False
