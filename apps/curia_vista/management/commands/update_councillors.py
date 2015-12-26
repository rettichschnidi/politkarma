from xml.etree import ElementTree
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import requests

from apps.curia_vista.models import Councillor


class Command(BaseCommand):
    help = 'Import councillors from parlament.ch'

    @transaction.atomic
    def handle(self, *args, **options):
        source_base = 'http://ws.parlament.ch/councillors?format=xml&lang=de&pagenumber='
        headers = {'User-Agent': 'Mozilla'}

        cur_page = 1
        while True:
            source = source_base + str(cur_page)
            cur_page += 1

            try:
                self.stdout.write("Starting importing from {}".format(source))
                response = requests.get(source, headers=headers)
            except Exception as e:
                raise CommandError("Could not fetch file from {}".format(source))

            councillors = ElementTree.fromstring(response.content)

            if not councillors:
                raise CommandError("Not a valid XML file: {}".format(source))

            more_pages = False
            for councillor in councillors:
                councillor_id = councillor.find('id').text
                councillor_updated = councillor.find('updated').text
                councillor_active = councillor.find('active').text
                councillor_code = councillor.find('code').text
                councillor_first_name = councillor.find('firstName').text
                councillor_last_name = councillor.find('lastName').text
                councillor_number = councillor.find('number').text if 'number' in councillor else None
                councillor_official_denomination = councillor.find('officialDenomination').text
                councillor_salutation_letter = councillor.find('salutationLetter').text
                councillor_salutation_title = councillor.find('salutationTitle').text
                if councillor.find('hasMorePages') is not None:
                    more_pages = 'true' == councillor.find('hasMorePages').text
                councillor_model = Councillor(id=councillor_id, updated=councillor_updated,
                                              active=councillor_active,
                                              code=councillor_code, first_name=councillor_first_name,
                                              last_name=councillor_last_name, number=councillor_number,
                                              official_denomination=councillor_official_denomination,
                                              salutation_letter=councillor_salutation_letter,
                                              salutation_title=councillor_salutation_title)
                councillor_model.save()
                print(councillor_model)
            self.stdout.write("Finished importing from {}".format(source))
            if not more_pages:
                break
        self.stdout.write("Done")
