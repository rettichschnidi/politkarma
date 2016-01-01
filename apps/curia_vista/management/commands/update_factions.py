from xml.etree import ElementTree

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.curia_vista.models import Faction


class Command(BaseCommand):
    help = 'Import factions from parlament.ch'

    @transaction.atomic
    def update(self, resource_url, lang, is_main):
        from django.utils import translation
        translation.activate(lang)
        url_template = resource_url + '?format=xml&lang=' + lang + '&pagenumber='
        headers = {'User-Agent': 'Mozilla'}
        cur_page = 1

        while True:
            cur_url = url_template + str(cur_page)
            cur_page += 1
            self.stdout.write("Importing: {}".format(cur_url))

            try:
                response = requests.get(cur_url, headers=headers)
            except Exception as e:
                raise CommandError("Could not fetch file from {}".format(cur_url))

            affair_summaries = ElementTree.fromstring(response.content)

            if not affair_summaries:
                raise CommandError("Not a valid XML file: {}".format(cur_url))

            more_pages = False
            for faction in affair_summaries:
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
                if is_main:
                    faction_model, created = Faction.objects.update_or_create(the_id=faction_id,
                                                                              from_date=faction_from_date,
                                                                              defaults={
                                                                                  'updated': faction_updated,
                                                                                  'abbreviation': faction_abbreviation,
                                                                                  'code': faction_code,
                                                                                  'from_date': faction_from_date,
                                                                                  'to_date': faction_to_date,
                                                                                  'name': faction_name,
                                                                                  'short_name': faction_short_name})
                else:
                    faction_model, created = Faction.objects.update_or_create(the_id=faction_id,
                                                                              updated=faction_updated,
                                                                              abbreviation=faction_abbreviation,
                                                                              code=faction_code,
                                                                              from_date=faction_from_date,
                                                                              to_date=faction_to_date,
                                                                              defaults={
                                                                                  'name': faction_name,
                                                                                  'short_name': faction_short_name
                                                                              })
                    assert not created

                faction_model.save()
                print(faction_model)

            self.stdout.write("Finished importing from {}".format(cur_url))
            if not more_pages:
                break
        self.stdout.write('Done language ' + lang)

    def handle(self, *args, **options):
        from politkarma import settings
        is_main = True
        resource_url = 'http://ws.parlament.ch/Factions/historic'
        for lang in [x[0] for x in settings.LANGUAGES]:
            self.update(resource_url, lang, is_main)
            is_main = False
