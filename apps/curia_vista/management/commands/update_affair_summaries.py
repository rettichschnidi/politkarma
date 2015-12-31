from xml.etree import ElementTree

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.curia_vista.models import *


class Command(BaseCommand):
    help = 'Import affair summaries from parlament.ch'

    @transaction.atomic
    def handle(self, *args, **options):
        source_base = 'http://ws.parlament.ch/affairsummaries?format=xml&lang=de&pagenumber='
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

            affair_summaries = ElementTree.fromstring(response.content)

            if not affair_summaries:
                raise CommandError("Not a valid XML file: {}".format(source))

            more_pages = False
            for affair_summary in affair_summaries:
                affair_summery_id = affair_summary.find('id').text
                affair_summery_updated = affair_summary.find('updated').text
                affair_summery_formatted_id = affair_summary.find('formattedId').text
                affair_summery_title = affair_summary.find('title').text
                if affair_summary.find('hasMorePages') is not None:
                    more_pages = 'true' == affair_summary.find('hasMorePages').text
                affair_summary_model, created = AffairSummary.objects.update_or_create(id=affair_summery_id,
                                                                                       defaults={
                                                                                           'formatted_id': affair_summery_formatted_id,
                                                                                           'updated': affair_summery_updated,
                                                                                           'title': affair_summery_title})
                affair_summary_model.full_clean()
                affair_summary_model.save()
                print(affair_summary_model)

            self.stdout.write("Finished importing from {}".format(source))
            if not more_pages:
                break
        self.stdout.write("Done")
