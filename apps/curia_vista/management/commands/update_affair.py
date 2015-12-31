from xml.etree import ElementTree

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.curia_vista.models import *


class Command(BaseCommand):
    help = 'Import cantons from parlament.ch'

    @transaction.atomic
    def handle(self, *args, **options):
        source_base = 'http://ws.parlament.ch/affairs?format=xml&lang=de&pagenumber='
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

            affairs = ElementTree.fromstring(response.content)

            if not affairs:
                raise CommandError("Not a valid XML file: {}".format(source))

            more_pages = False
            for affair in affairs:
                affair_id = affair.find('id').text
                affair_updated = affair.find('updated').text
                canton_short_id = affair.find('shortId').text
                if affair.find('hasMorePages') is not None:
                    more_pages = 'true' == affair.find('hasMorePages').text
                affair_model, created = Affair.objects.update_or_create(id=affair_id,
                                                                        defaults={'short_id': canton_short_id,
                                                                                  'updated': affair_updated})
                affair_model.full_clean()
                affair_model.save()
                print(affair_model)

            self.stdout.write("Finished importing from {}".format(source))
            if not more_pages:
                break
        self.stdout.write("Done")
