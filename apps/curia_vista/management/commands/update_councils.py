from xml.etree import ElementTree
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import requests

from apps.curia_vista.models import *


class Command(BaseCommand):
    help = 'Import counils from parlament.ch'

    @transaction.atomic
    def handle(self, *args, **options):
        source = 'http://ws.parlament.ch/councils?format=xml&lang=de'
        headers = {'User-Agent': 'Mozilla'}

        self.stdout.write("Importing: {}".format(source))

        try:
            response = requests.get(source, headers=headers)
        except Exception as e:
            raise CommandError("Could not fetch file from {}".format(source))

        councils = ElementTree.fromstring(response.content)

        if not councils:
            raise CommandError("Not a valid XML file: {}".format(source))

        for council in councils:
            council_id = council.find('id').text
            council_updated = council.find('updated').text
            council_abbreviation = council.find('abbreviation').text
            council_code = council.find('code').text
            council_type = council.find('type').text
            if council.find('hasMorePages') is not None:
                assert 'false' == council.find('hasMorePages').text
            council_model, created = Council.objects.update_or_create(id=council_id,
                                                                      defaults={'updated': council_updated,
                                                                                'abbreviation': council_abbreviation,
                                                                                'code': council_code,
                                                                                'type': council_type})
            council_model.full_clean()
            council_model.save()
            print(council_model)
