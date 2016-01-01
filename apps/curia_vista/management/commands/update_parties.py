from xml.etree import ElementTree

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.curia_vista.models import *


class Command(BaseCommand):
    help = 'Import parties from parlament.ch'

    @transaction.atomic
    def handle(self, *args, **options):
        source_base = 'http://ws.parlament.ch/Parties/historic?format=xml&lang=de&pagenumber='
        headers = {'User-Agent': 'Mozilla'}
        cur_page = 1

        while True:
            source = source_base + str(cur_page)
            cur_page += 1
            self.stdout.write("Importing: {}".format(source))

            try:
                response = requests.get(source, headers=headers)
            except Exception as e:
                raise CommandError("Could not fetch file from {}".format(source))

            parties = ElementTree.fromstring(response.content)

            if not parties:
                raise CommandError("Not a valid XML file: {}".format(source))

            more_pages = False
            for party in parties:
                party_id = party.find('id').text
                party_updated = party.find('updated').text
                party_abbreviation = party.find('abbreviation').text
                party_code = party.find('code').text
                party_name = party.find('name').text
                if party.find('hasMorePages') is not None:
                    more_pages = 'true' == party.find('hasMorePages').text
                party_model, created = Party.objects.update_or_create(id=party_id,
                                                                      defaults={'updated': party_updated,
                                                                                'abbreviation': party_abbreviation,
                                                                                'code': party_code,
                                                                                'name': party_name})
                party_model.full_clean()
                party_model.save()
                print(party_model)

            self.stdout.write("Finished importing from {}".format(source))
            if not more_pages:
                break
        self.stdout.write("Done")
