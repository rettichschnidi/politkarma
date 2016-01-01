from xml.etree import ElementTree

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.curia_vista.models import Party


class Command(BaseCommand):
    help = 'Import parties from parlament.ch'

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
            for party in affair_summaries:
                party_id = party.find('id').text
                party_updated = party.find('updated').text
                party_abbreviation = party.find('abbreviation').text
                party_code = party.find('code').text
                party_name = party.find('name').text
                if party.find('hasMorePages') is not None:
                    more_pages = 'true' == party.find('hasMorePages').text
                if is_main:
                    party_model, created = Party.objects.update_or_create(id=party_id,
                                                                          defaults={
                                                                              'updated': party_updated,
                                                                              'abbreviation': party_abbreviation,
                                                                              'code': party_code,
                                                                              'name': party_name})
                else:
                    party_model, created = Party.objects.update_or_create(id=party_id,
                                                                          updated=party_updated,
                                                                          code=party_code,
                                                                          defaults={
                                                                              'name': party_name,
                                                                              'abbreviation': party_abbreviation
                                                                          })
                    assert not created

                party_model.save()
                print(party_model)

            self.stdout.write("Finished importing from {}".format(cur_url))
            if not more_pages:
                break
        self.stdout.write('Done language ' + lang)

    def handle(self, *args, **options):
        from politkarma import settings
        is_main = True
        resource_url = 'http://ws.parlament.ch/Parties/historic'
        for lang in [x[0] for x in settings.LANGUAGES]:
            self.update(resource_url, lang, is_main)
            is_main = False
