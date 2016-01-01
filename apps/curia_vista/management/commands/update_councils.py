from xml.etree import ElementTree
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import requests

from apps.curia_vista.models import *
from politkarma import settings


class Command(BaseCommand):
    help = 'Import councils from parlament.ch'

    def update(self, resource_url, lang, is_main):
        from django.utils import translation
        assert lang in [x[0] for x in settings.LANGUAGES]
        translation.activate(lang)
        url = resource_url + '?format=xml&lang=' + lang

        self.stdout.write("Importing {}".format(url))

        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla'})
        except Exception as e:
            raise CommandError("Could not fetch file from {}".format(url))

        councils = ElementTree.fromstring(response.content)

        if not councils:
            raise CommandError("Not a valid XML file: {}".format(url))

        for council in councils:
            council_id = council.find('id').text
            council_updated = council.find('updated').text
            council_abbreviation = council.find('abbreviation').text
            council_code = council.find('code').text
            council_name = council.find('name').text
            council_type = council.find('type').text
            if council.find('hasMorePages') is not None:
                assert 'false' == council.find('hasMorePages').text
            if is_main:
                council_model, created = Council.objects.update_or_create(id=council_id,
                                                                          defaults={'updated': council_updated,
                                                                                    'name': council_name,
                                                                                    'abbreviation': council_abbreviation,
                                                                                    'code': council_code,
                                                                                    'type': council_type})
            else:
                council_model, created = Council.objects.update_or_create(id=council_id, updated=council_updated,
                                                                          type=council_type, code=council_code,
                                                                          defaults={
                                                                              'name': council_name,
                                                                              'abbreviation': council_abbreviation,
                                                                          })
                assert not created
            council_model.full_clean()
            council_model.save()
            print(council_model)

    @transaction.atomic
    def handle(self, *args, **options):
        is_main = True
        resource_url = 'http://ws.parlament.ch/councils'
        for lang in [x[0] for x in settings.LANGUAGES]:
            self.update(resource_url, lang, is_main)
            is_main = False
