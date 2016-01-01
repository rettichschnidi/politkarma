from xml.etree import ElementTree

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.curia_vista.models import Session
from politkarma import settings


class Command(BaseCommand):
    help = 'Import sessions from parlament.ch'

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
            for session in affair_summaries:
                session_updated = session.find('updated').text
                session_code = session.find('code').text
                session_from_date = session.find('from').text
                session_to_date = session.find('to').text
                session_name = session.find('name').text
                if session.find('hasMorePages') is not None:
                    more_pages = 'true' == session.find('hasMorePages').text
                if is_main:
                    session_model, created = Session.objects.update_or_create(code=session_code,
                                                                              defaults={'updated': session_updated,
                                                                                        'from_date': session_from_date,
                                                                                        'to_date': session_to_date,
                                                                                        'name': session_name})
                else:
                    session_model, created = Session.objects.update_or_create(code=session_code,
                                                                              updated=session_updated,
                                                                              from_date=session_from_date,
                                                                              to_date=session_to_date,
                                                                              defaults={
                                                                                  'name': session_name
                                                                              })
                    assert not created
                session_model.save()
                print(session_model)

            self.stdout.write("Finished importing from {}".format(cur_url))
            if not more_pages:
                break
        self.stdout.write('Done language ' + lang)

    def handle(self, *args, **options):
        is_main = True
        resource_url = 'http://ws.parlament.ch/Sessions'
        for lang in [x[0] for x in settings.LANGUAGES]:
            self.update(resource_url, lang, is_main)
            is_main = False
