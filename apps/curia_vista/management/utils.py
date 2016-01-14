from xml.etree import ElementTree

import requests
from django.core.management import CommandError
from django.db import transaction

from politkarma import settings


def xml_from_url(url, page_num):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla'})
    except Exception as e:
        raise CommandError("Could not fetch XML data from '{}'".format(url))

    xml = ElementTree.fromstring(response.content)

    if not xml:
        raise CommandError("Invalid XML data: {}".format(url))
    return xml


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
    url = settings.WEBSERVICE_URL + configuration['resource_path'] + '?format=xml&lang=' + language
    xml_root = xml_from_url(url, 0)
    model_class = configuration['model_class']

    for element in xml_root:
        defaults = {}
        values = {}
        for tag, mapping in configuration['mapping'].items():
            assert not (mapping.primary and mapping.translated)

            if mapping.translated or (is_main_language and not mapping.primary):
                target = defaults
            else:
                target = values

            # Allow tags to be missing if explicitly specified
            try:
                value = element.find(tag).text
            except AttributeError as e:
                if not mapping.null:
                    raise CommandError(str(e))
                value = None

            # Allow simple foreign-key-relation
            if mapping.fk_type and value:
                value = mapping.fk_type.objects.get(id=value)

            target[mapping.model_column_name or tag] = value

            if element.find('hasMorePages') is not None:
                assert 'false' == element.find('hasMorePages').text
        model, created = model_class.objects.update_or_create(defaults=defaults, **values)
        assert True if is_main_language else not created
        model.full_clean()
        model.save()
        command.stdout.write(str(model))
