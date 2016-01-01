from xml.etree import ElementTree
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from politkarma import settings
import requests

from apps.curia_vista.models import Department


class Command(BaseCommand):
    help = 'Import departments from parlament.ch'

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

        departments = ElementTree.fromstring(response.content)

        if not departments:
            raise CommandError("Not a valid XML file: {}".format(url))

        for department in departments:
            department_id = department.find('id').text
            department_updated = department.find('updated').text
            department_abbreviation = department.find('abbreviation').text
            department_code = department.find('code').text
            department_name = department.find('name').text
            if department.find('hasMorePages') is not None:
                assert 'false' == department.find('hasMorePages').text
            if is_main:
                department_model, created = Department.objects.update_or_create(id=department_id,
                                                                                defaults={'updated': department_updated,
                                                                                          'name': department_name,
                                                                                          'abbreviation': department_abbreviation,
                                                                                          'code': department_code})
            else:
                department_model, created = Department.objects.update_or_create(id=department_id,
                                                                                updated=department_updated,
                                                                                code=department_code,
                                                                                defaults={
                                                                                    'name': department_name,
                                                                                    'abbreviation': department_abbreviation,
                                                                                })
                assert not created
            department_model.full_clean()
            department_model.save()
            print(department_model)

    def handle(self, *args, **options):
        is_main = True
        resource_url = 'http://ws.parlament.ch/Departments'
        for lang in [x[0] for x in settings.LANGUAGES]:
            self.update(resource_url, lang, is_main)
            is_main = False
