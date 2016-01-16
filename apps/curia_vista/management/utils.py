import requests
from django.core.management import CommandError
from django.db import transaction
import json
from politkarma import settings


def xml_from_url(command, url):
    command.stdout.write("Processing: " + url)
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla'})
    except Exception as e:
        raise CommandError("Could not fetch XML data from '{}'".format(url))

    try:
        text_data = response.content.decode('UTF-8')
        data_dict = json.loads(text_data)
        return data_dict
    except Exception as e:
        raise CommandError("Invalid JSON data from '{}': {}".format(url, e))


class Config:
    def __init__(self, translated=False, model_column_name='', primary=False, fk_type=None, null=False):
        self.translated = translated
        self.model_column_name = model_column_name
        self.primary = primary
        self.fk_type = fk_type
        self.null = null


@transaction.atomic
def update_from_webservice(command, configuration, language, is_main_language):
    from django.utils import translation
    translation.activate(language)
    model_class = configuration['model_class']

    page_number = 1
    has_more = True
    while has_more:
        url = "{}{}?format=json&lang={}&pageNumber={}".format(settings.WEBSERVICE_URL, configuration['resource_path'],
                                                              language, page_number)
        root = xml_from_url(command, url)
        for element in root:
            defaults = {}
            values = {}
            for tag, mapping in configuration['mapping'].items():
                assert not (mapping.primary and mapping.translated)

                # Allow tags to be missing if explicitly specified
                try:
                    value = element[tag]
                except AttributeError as e:
                    if not mapping.null:
                        raise CommandError(str(e))
                    value = None

                # Allow simple foreign-key-relation
                if mapping.fk_type and value:
                    value = mapping.fk_type.objects.get(id=value)

                # Decide which dict to put values into
                if mapping.translated or (is_main_language and not mapping.primary):
                    target = defaults
                else:
                    target = values

                target[mapping.model_column_name or tag] = value

            model, created = model_class.objects.update_or_create(defaults=defaults, **values)
            assert True if is_main_language else not created
            model.full_clean()
            model.save()

        has_more = 'hasMorePages' in root[-1] and root[-1]['hasMorePages']
        if has_more:
            page_number += 1
            assert configuration['has_more']
