from xml.etree import ElementTree

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.curia_vista.models import AffairState
from politkarma import settings


class Command(BaseCommand):
    help = 'Import affair states from parlament.ch'

    def update(self, resource_url, lang, is_main):
        from django.utils import translation
        translation.activate(lang)
        url = resource_url + '?format=xml&lang=' + lang

        self.stdout.write("Importing {}".format(url))

        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla'})
        except Exception as e:
            raise CommandError("Could not fetch file from {}".format(url))

        affair_states = ElementTree.fromstring(response.content)

        if not affair_states:
            raise CommandError("Not a valid XML file: {}".format(url))

        for affair_state in affair_states:
            affair_state_id = affair_state.find('id').text
            affair_state_updated = affair_state.find('updated').text
            affair_state_code = affair_state.find('code').text
            affair_state_name = affair_state.find('name').text
            affair_state_sorting = affair_state.find('sorting').text
            affair_state_parent = None
            if affair_state.find('parent') is not None:
                affair_state_parent = AffairState.objects.get(pk=affair_state.find('parent').find('id').text)
                assert affair_state_parent is not None

            if affair_state.find('hasMorePages') is not None:
                assert 'false' == affair_state.find('hasMorePages').text

            if is_main:
                affair_state_model, created = AffairState.objects.update_or_create(id=affair_state_id,
                                                                                   defaults={
                                                                                       'updated': affair_state_updated,
                                                                                       'name': affair_state_name,
                                                                                       'sorting': affair_state_sorting,
                                                                                       'parent': affair_state_parent,
                                                                                       'code': affair_state_code})
            else:
                affair_state_model, created = AffairState.objects.update_or_create(id=affair_state_id,
                                                                                   updated=affair_state_updated,
                                                                                   code=affair_state_code,
                                                                                   sorting=affair_state_sorting,
                                                                                   parent=affair_state_parent,
                                                                                   defaults={
                                                                                       'name': affair_state_name
                                                                                   })
                assert not created
            affair_state_model.full_clean()
            affair_state_model.save()
            print(affair_state_model)

    @transaction.atomic
    def handle(self, *args, **options):
        is_main = True
        resource_url = 'http://ws.parlament.ch/affairs/states'
        for lang in [x[0] for x in settings.LANGUAGES]:
            self.update(resource_url, lang, is_main)
            is_main = False
