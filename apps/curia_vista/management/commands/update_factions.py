from xml.etree import ElementTree

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.curia_vista.models import *


class Command(BaseCommand):
    help = 'Import factions from parlament.ch'

    @transaction.atomic
    def handle(self, *args, **options):
        source_base = 'http://ws.parlament.ch/Factions/historic?format=xml&lang=de&pagenumber='
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

            factions = ElementTree.fromstring(response.content)

            if not factions:
                raise CommandError("Not a valid XML file: {}".format(source))

            more_pages = False
            for faction in factions:
                faction_id = faction.find('id').text
                faction_updated = faction.find('updated').text
                faction_abbreviation = faction.find('abbreviation').text
                faction_code = faction.find('code').text
                faction_from_date = faction.find('from').text
                faction_to_date = None if faction.find('to') is None else faction.find('to').text
                faction_name = faction.find('name').text
                faction_short_name = faction.find('shortName').text
                if faction.find('hasMorePages') is not None:
                    more_pages = 'true' == faction.find('hasMorePages').text
                faction_model, created = Faction.objects.update_or_create(id=faction_id,
                                                                          defaults={
                                                                              'updated': faction_updated,
                                                                              'abbreviation': faction_abbreviation,
                                                                              'code': faction_code,
                                                                              'from_date': faction_from_date,
                                                                              'to_date': faction_to_date,
                                                                              'name': faction_name,
                                                                              'short_name': faction_short_name})
                faction_model.full_clean()
                faction_model.save()
                print(faction_model)

            self.stdout.write("Finished importing from {}".format(source))
            if not more_pages:
                break
        self.stdout.write("Done")
