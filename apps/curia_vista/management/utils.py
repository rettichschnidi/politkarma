import requests
from django.core.management import CommandError
from django.db import transaction
import json

from apps.curia_vista import models
from politkarma import settings


def xml_from_url(command, url):
    command.stdout.write("Processing: " + url)
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla'})
    except Exception as e:
        raise CommandError("Could not fetch data from '{}'".format(url))

    try:
        text_data = response.content.decode('UTF-8')
        data_dict = json.loads(text_data)
        return data_dict
    except Exception as e:
        raise CommandError("Invalid JSON data from '{}': {}".format(url, e))


class Config:
    def __init__(self, translated=False, model_column_name='', primary=False, fk_type=None, null=False, default=None,
                 sub_keys=[]):
        """
            Configuration object to describe the mapping between JSON and Django model.
            Note to myself: Most likely big-time NIH syndrome here...
        :param translated: Is this field translated using django-modeltranslation?
        :param model_column_name: If the JSON name differs from the django column name, specify this it here
        :param primary: True if this field is part of the table key
        :param fk_type: If specified, this is the class of the foreign key model. ATM always matched on the id field.
        :param null: True if the JSON attribute may no exist
        :param default: Value to feed Django model with if value not specified in JSON
        :param sub_keys: A list of strings to specify a value nested in the JSON
        """
        self.translated = translated
        self.model_column_name = model_column_name
        self.primary = primary
        self.fk_type = fk_type
        self.null = null
        self.sub_keys = sub_keys
        self.default = default


@transaction.atomic
def update_from_webservice(command, configuration, language, is_update):
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
                    for sub_key in mapping.sub_keys:
                        value = value[sub_key]
                except Exception as e:
                    if not mapping.null:
                        raise CommandError(str(e))
                    value = mapping.default

                    # Allow simple foreign-key-relation
                if mapping.fk_type and value:
                    try:
                        value = mapping.fk_type.objects.get(id=value)
                    except mapping.fk_type.DoesNotExist as e:
                        raise CommandError("'{}' is not a valid id for '{}'".format(value, str(mapping.fk_type)))

                # Decide which dict to put values into
                if not mapping.primary and (mapping.translated or is_update):
                    target = defaults
                else:
                    target = values

                target[mapping.model_column_name or tag] = value

            model, created = model_class.objects.update_or_create(defaults=defaults, **values)
            if is_update and created:
                raise CommandError("Accidentally created: {}".format(model))
            model.full_clean()
            model.save()

        has_more = 'hasMorePages' in root[-1] and root[-1]['hasMorePages']
        if has_more:
            page_number += 1
            assert configuration['has_more']
