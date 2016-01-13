from xml.etree import ElementTree

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.curia_vista.models import AffairType
from politkarma import settings


class Command(BaseCommand):
    help = 'Import affair types from parlament.ch'

    def update(self, resource_url, lang, is_main):
        from django.utils import translation
        translation.activate(lang)
        url = resource_url + '?format=xml&lang=' + lang

        self.stdout.write("Importing {}".format(url))

        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla'})
        except Exception as e:
            raise CommandError("Could not fetch file from {}".format(url))

        affair_types = ElementTree.fromstring(response.content)

        if not affair_types:
            raise CommandError("Not a valid XML file: {}".format(url))

        for affair_type in affair_types:
            affair_type_id = affair_type.find('id').text
            affair_type_updated = affair_type.find('updated').text
            affair_type_code = affair_type.find('code').text
            affair_type_name = affair_type.find('name').text
            if affair_type.find('hasMorePages') is not None:
                assert 'false' == affair_type.find('hasMorePages').text
            if is_main:
                affair_type_model, created = AffairType.objects.update_or_create(id=affair_type_id,
                                                                                 defaults={
                                                                                     'updated': affair_type_updated,
                                                                                     'name': affair_type_name,
                                                                                     'code': affair_type_code})
            else:
                affair_type_model, created = AffairType.objects.update_or_create(id=affair_type_id,
                                                                                 updated=affair_type_updated,
                                                                                 code=affair_type_code,
                                                                                 defaults={
                                                                                     'name': affair_type_name
                                                                                 })
                assert not created
            affair_type_model.full_clean()
            affair_type_model.save()
            self.stdout.write(str(affair_type_model))

    @transaction.atomic
    def handle(self, *args, **options):
        is_main = True
        resource_url = 'http://ws.parlament.ch/affairs/types'
        for lang in [x[0] for x in settings.LANGUAGES]:
            self.update(resource_url, lang, is_main)
            is_main = False
