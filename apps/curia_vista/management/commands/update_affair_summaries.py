from xml.etree import ElementTree

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from politkarma import settings

from apps.curia_vista.models import *


class Command(BaseCommand):
    help = 'Import affair summaries from parlament.ch'

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
            for affair_summary in affair_summaries:
                affair_summery_id = affair_summary.find('id').text
                affair_summery_updated = affair_summary.find('updated').text
                affair_summery_formatted_id = affair_summary.find('formattedId').text
                affair_summery_title = affair_summary.find('title').text
                if affair_summary.find('hasMorePages') is not None:
                    more_pages = 'true' == affair_summary.find('hasMorePages').text
                if is_main:
                    affair_summary_model, created = AffairSummary.objects.update_or_create(id=affair_summery_id,
                                                                                           defaults={
                                                                                               'updated': affair_summery_updated,
                                                                                               'formatted_id': affair_summery_formatted_id,
                                                                                               'title': affair_summery_title})
                else:
                    affair_summary_model, created = AffairSummary.objects.update_or_create(id=affair_summery_id,
                                                                                           updated=affair_summery_updated,
                                                                                           formatted_id=affair_summery_formatted_id,
                                                                                           defaults={
                                                                                               'title': affair_summery_title
                                                                                           })
                    assert not created

                affair_summary_model.full_clean()
                affair_summary_model.save()
                print(affair_summary_model)

            self.stdout.write("Finished importing from {}".format(cur_url))
            if not more_pages:
                break
        self.stdout.write("Done")

    def handle(self, *args, **options):
        is_main = True
        resource_url = 'http://ws.parlament.ch/affairsummaries'
        for lang in [x[0] for x in settings.LANGUAGES]:
            self.update(resource_url, lang, is_main)
            is_main = False
