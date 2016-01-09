from xml.etree import ElementTree

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.curia_vista.models import AffairTopic
from politkarma import settings


class Command(BaseCommand):
    help = 'Import affair topics from parlament.ch'

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

        affair_topics = ElementTree.fromstring(response.content)

        if not affair_topics:
            raise CommandError("Not a valid XML file: {}".format(url))

        for affair_topic in affair_topics:
            affair_topic_id = affair_topic.find('id').text
            affair_topic_updated = affair_topic.find('updated').text
            affair_topic_code = affair_topic.find('code').text
            affair_topic_name = affair_topic.find('name').text
            if affair_topic.find('hasMorePages') is not None:
                assert 'false' == affair_topic.find('hasMorePages').text
            if is_main:
                affair_topic_model, created = AffairTopic.objects.update_or_create(id=affair_topic_id,
                                                                                   defaults={
                                                                                       'updated': affair_topic_updated,
                                                                                       'name': affair_topic_name,
                                                                                       'code': affair_topic_code})
            else:
                affair_topic_model, created = AffairTopic.objects.update_or_create(id=affair_topic_id,
                                                                                   updated=affair_topic_updated,
                                                                                   code=affair_topic_code,
                                                                                   defaults={
                                                                                       'name': affair_topic_name
                                                                                   })
                assert not created
            affair_topic_model.full_clean()
            affair_topic_model.save()
            print(affair_topic_model)

    @transaction.atomic
    def handle(self, *args, **options):
        is_main = True
        resource_url = 'http://ws.parlament.ch/affairs/topics'
        for lang in [x[0] for x in settings.LANGUAGES]:
            self.update(resource_url, lang, is_main)
            is_main = False
