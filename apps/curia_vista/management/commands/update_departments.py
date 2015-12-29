from xml.etree import ElementTree
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import requests

from apps.curia_vista.models import *


class Command(BaseCommand):
    help = 'Import departments from parlament.ch'

    @transaction.atomic
    def handle(self, *args, **options):
        source = 'http://ws.parlament.ch/Departments?format=xml&lang=de'
        headers = {'User-Agent': 'Mozilla'}

        self.stdout.write("Importing: {}".format(source))

        try:
            response = requests.get(source, headers=headers)
        except Exception as e:
            raise CommandError("Could not fetch file from {}".format(source))

        departments = ElementTree.fromstring(response.content)

        if not departments:
            raise CommandError("Not a valid XML file: {}".format(source))

        for department in departments:
            department_id = department.find('id').text
            department_updated = department.find('updated').text
            department_code = department.find('code').text
            department_model, created = Department.objects.update_or_create(id=department_id,
                                                                            defaults={'updated': department_updated,
                                                                                      'code': department_code})
            department_model.full_clean()
            department_model.save()
            print(department_model)
