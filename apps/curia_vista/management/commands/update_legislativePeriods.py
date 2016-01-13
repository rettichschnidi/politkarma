from xml.etree import ElementTree
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from politkarma import settings
import requests

from apps.curia_vista.models import LegislativePeriod


class Command(BaseCommand):
    help = 'Import legislative periods from parlament.ch'

    @transaction.atomic
    def update(self, resource_url, lang, is_main):
        from django.utils import translation
        translation.activate(lang)
        url = resource_url + '?format=xml&lang=' + lang

        self.stdout.write("Importing {}".format(url))

        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla'})
        except Exception as e:
            raise CommandError("Could not fetch file from {}".format(url))

        periods = ElementTree.fromstring(response.content)

        if not periods:
            raise CommandError("Not a valid XML file: {}".format(url))

        for period in periods:
            period_id = period.find('id').text
            period_updated = period.find('updated').text
            period_code = period.find('code').text
            period_from = period.find('from').text
            period_name = period.find('name').text
            period_to = period.find('to').text
            if period.find('hasMorePages') is not None:
                assert 'false' == period.find('hasMorePages').text
            if is_main:
                period_model, created = LegislativePeriod.objects.update_or_create(id=period_id,
                                                                                   defaults={'updated': period_updated,
                                                                                             'code': period_code,
                                                                                             'from_date': period_from,
                                                                                             'name': period_name,
                                                                                             'to_date': period_to})
            else:
                period_model, created = LegislativePeriod.objects.update_or_create(id=period_id,
                                                                                   updated=period_updated,
                                                                                   code=period_code,
                                                                                   from_date=period_from,
                                                                                   to_date=period_to,
                                                                                   defaults={
                                                                                       'name': period_name
                                                                                   })
                assert not created
            period_model.full_clean()
            period_model.save()
            self.stdout.write(str(period_model))

    def handle(self, *args, **options):
        is_main = True
        resource_url = 'http://ws.parlament.ch/LegislativePeriods'
        for lang in [x[0] for x in settings.LANGUAGES]:
            self.update(resource_url, lang, is_main)
            is_main = False
