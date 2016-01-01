from xml.etree import ElementTree

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.curia_vista.models import Committee, Council


class Command(BaseCommand):
    help = 'Import committees from parlament.ch. Requires councils to be updated/imported.'

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

            committees = ElementTree.fromstring(response.content)

            if not committees:
                raise CommandError("Not a valid XML file: {}".format(cur_url))

            more_pages = False
            for committee in committees:
                committee_id = committee.find('id').text
                committee_updated = committee.find('updated').text
                committee_abbreviation = committee.find('abbreviation').text
                committee_code = committee.find('code').text
                committee_number = committee.find('committeeNumber').text
                committee_council_id = committee.find('council').find('id').text
                committee_council_model = Council.objects.get(id=committee_council_id)
                committee_from_date = committee.find('from').text
                committee_is_active = committee.find('isActive') is not None and committee.find(
                    'isActive').text == 'true'
                committee_name = committee.find('name').text
                committee_sub_number = None if committee.find('subcommitteeNumber') is None else committee.find(
                        'subcommitteeNumber').text
                committee_to_date = None if committee.find('to') is None else committee.find('to').text
                committee_type_code = committee.find('typeCode').text
                if committee.find('hasMorePages') is not None:
                    more_pages = 'true' == committee.find('hasMorePages').text
                if is_main:
                    committee_model, created = Committee.objects.update_or_create(id=committee_id,
                                                                                  defaults={
                                                                                      'updated': committee_updated,
                                                                                      'abbreviation': committee_abbreviation,
                                                                                      'code': committee_code,
                                                                                      'number': committee_number,
                                                                                      'council': committee_council_model,
                                                                                      'from_date': committee_from_date,
                                                                                      'is_active': committee_is_active,
                                                                                      'name': committee_name,
                                                                                      'sub_number': committee_sub_number,
                                                                                      'to_date': committee_to_date,
                                                                                      'type_code': committee_type_code})
                else:
                    committee_model, created = Committee.objects.update_or_create(id=committee_id,
                                                                                  updated=committee_updated,
                                                                                  code=committee_code,
                                                                                  number=committee_number,
                                                                                  council=committee_council_model,
                                                                                  from_date=committee_from_date,
                                                                                  is_active=committee_is_active,
                                                                                  sub_number=committee_sub_number,
                                                                                  to_date=committee_to_date,
                                                                                  type_code=committee_type_code,
                                                                                  defaults={
                                                                                      'abbreviation': committee_abbreviation,
                                                                                      'name': committee_name
                                                                                  })
                    assert not created

                committee_model.save()
                print(committee_model)

            self.stdout.write("Finished importing from {}".format(cur_url))
            if not more_pages:
                break
        self.stdout.write('Done language ' + lang)

    def handle(self, *args, **options):
        from politkarma import settings
        is_main = True
        resource_url = 'http://ws.parlament.ch/committees/'
        for lang in [x[0] for x in settings.LANGUAGES]:
            self.update(resource_url, lang, is_main)
            is_main = False
