from xml.etree import ElementTree
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import requests

from apps.curia_vista.models import *


class Command(BaseCommand):
    help = 'Import leg_periods from parlament.ch'

    @transaction.atomic
    def handle(self, *args, **options):
        source = 'http://ws.parlament.ch/LegislativePeriods?format=xml&lang=de'
        headers = {'User-Agent': 'Mozilla'}

        self.stdout.write("Importing: {}".format(source))

        try:
            response = requests.get(source, headers=headers)
        except Exception as e:
            raise CommandError("Could not fetch file from {}".format(source))

        periods = ElementTree.fromstring(response.content)

        if not periods:
            raise CommandError("Not a valid XML file: {}".format(source))

        for period in periods:
            leg_period_id = period.find('id').text
            leg_period_updated = period.find('updated').text
            leg_period_code = period.find('code').text
            leg_period_from_date = period.find('from').text
            leg_period_to_date = period.find('to').text
            leg_period_model, created = LegislativePeriod.objects.update_or_create(id=leg_period_id,
                                                                                   defaults={
                                                                                       'updated': leg_period_updated,
                                                                                       'code': leg_period_code,
                                                                                       'from_date': leg_period_from_date,
                                                                                       'to_date': leg_period_to_date})
            leg_period_model.full_clean()
            leg_period_model.save()
            print(leg_period_model)
