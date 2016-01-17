from django.core.management.base import BaseCommand

from apps.curia_vista.management.utils import Config, update_from_webservice
from politkarma import settings

import apps.curia_vista.models

configurations = {
    'Canton': {
        'model_class': apps.curia_vista.models.Canton,
        'resource_path': '/cantons',
        'has_more': False,
        'mapping': {
            'id': Config(primary=True),
            'updated': Config(),
            'abbreviation': Config(translated=True),
            'code': Config(),
            'name': Config(translated=True)
        }
    },
    'Department': {
        'model_class': apps.curia_vista.models.Department,
        'resource_path': '/departments',
        'has_more': False,
        'mapping': {
            'id': Config(primary=True),
            'updated': Config(),
            'abbreviation': Config(translated=True),
            'code': Config(),
            'name': Config(translated=True)
        }
    },
    'Council': {
        'model_class': apps.curia_vista.models.Council,
        'resource_path': '/councils',
        'has_more': False,
        'mapping': {
            'id': Config(primary=True),
            'updated': Config(),
            'abbreviation': Config(translated=True),
            'code': Config(),
            'name': Config(translated=True),
            'type': Config(),
        }
    },
    'AffairTopic': {
        'model_class': apps.curia_vista.models.AffairTopic,
        'resource_path': '/affairs/topics',
        'has_more': False,
        'mapping': {
            'id': Config(primary=True),
            'updated': Config(),
            'code': Config(),
            'name': Config(translated=True),
        }
    },
    'AffairType': {
        'model_class': apps.curia_vista.models.AffairType,
        'resource_path': '/affairs/types',
        'has_more': False,
        'mapping': {
            'id': Config(primary=True),
            'updated': Config(),
            'code': Config(),
            'name': Config(translated=True),
        }
    },
    'AffairState': {
        'model_class': apps.curia_vista.models.AffairState,
        'resource_path': '/affairs/states',
        'has_more': False,
        'mapping': {
            'id': Config(primary=True),
            'updated': Config(),
            'code': Config(),
            'sorting': Config(),
            'parent.id': Config(fk_type=apps.curia_vista.models.AffairState, model_column_name='parent', null=True),
            'name': Config(translated=True),
        }
    },
    'LegislativePeriod': {
        'model_class': apps.curia_vista.models.LegislativePeriod,
        'resource_path': '/legislativeperiods',
        'has_more': False,
        'mapping': {
            'id': Config(primary=True),
            'updated': Config(),
            'code': Config(),
            'from': Config(model_column_name='from_date'),
            'name': Config(translated=True),
            'to': Config(model_column_name='to_date'),
        }
    },
    'Affair': {
        'model_class': apps.curia_vista.models.Affair,
        'resource_path': '/affairs',
        'has_more': True,
        'mapping': {
            'id': Config(primary=True),
            'updated': Config(),
            'shortId': Config(model_column_name='short_id'),
        }
    },
    'Session': {
        'model_class': apps.curia_vista.models.Session,
        'resource_path': '/sessions',
        'has_more': True,
        'mapping': {
            'code': Config(primary=True),
            'updated': Config(),
            'from': Config(model_column_name='from_date'),
            'name': Config(translated=True),
            'to': Config(model_column_name='to_date'),
        }
    }
}


class Command(BaseCommand):
    help = 'Update local Curia Vista data using ws.parlament.ch'
    languages = [x[0] for x in settings.LANGUAGES]

    def add_arguments(self, parser):
        parser.add_argument('--models', nargs='+', help="Limit update to specified models", type=str)
        parser.add_argument('--main-only', dest='main_only', action='store_true',
                            help="Limit update to the main language ({})".format(Command.languages[0]),
                            default=False)
        parser.add_argument('--show-models', action='store_true', dest='show_models', default=False,
                            help='List available Django models')

    def handle(self, *args, **options):
        if options['show_models']:
            jobs = ", ".join(configurations)
            self.stdout.write("Available jobs:")
            for j in configurations:
                self.stdout.write(" - " + j)
            return

        if options['models']:
            unwanted = configurations.keys() - set(options['models'])
            for unwanted_key in unwanted: del configurations[unwanted_key]

        for model_name, config in configurations.items():
            self.stdout.write("Updating data for model '{}'".format(model_name))
            if options['main_only']:
                update_from_webservice(self, config, Command.languages[0], True)
            else:
                for index, language in enumerate(Command.languages):
                    update_from_webservice(self, config, language, index == 0)
