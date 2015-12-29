from xml.etree import ElementTree
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import requests

from apps.curia_vista.models import *


class Command(BaseCommand):
    help = 'Import cantons from parlament.ch'

    @transaction.atomic
    def handle(self, *args, **options):
        source = 'http://ws.parlament.ch/cantons?format=xml&lang=de'
        headers = {'User-Agent': 'Mozilla'}

        self.stdout.write("Importing: {}".format(source))

        try:
            response = requests.get(source, headers=headers)
        except Exception as e:
            raise CommandError("Could not fetch file from {}".format(source))

        cantons = ElementTree.fromstring(response.content)

        if not cantons:
            raise CommandError("Not a valid XML file: {}".format(source))

        for canton in cantons:
            canton_id = canton.find('id').text
            canton_updated = canton.find('updated').text
            canton_code = canton.find('code').text
            canton_model, created = Canton.objects.update_or_create(id=canton_id, defaults={'updated': canton_updated,
                                                                                            'code': canton_code})
            canton_model.full_clean()
            canton_model.save()
            print(canton_model)
