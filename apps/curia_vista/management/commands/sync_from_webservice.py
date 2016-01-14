from django.core.management.base import BaseCommand

from apps.curia_vista.management.utils import Config, update_from_webservice
from politkarma import settings

from apps.curia_vista.models import Canton, Department, Council, AffairTopic, AffairType, LegislativePeriod, AffairState

configurations = {
    'Canton': {
        'model_class': Canton,
        'resource_path': '/cantons',
        'mapping': {
            'id': Config(primary=True),
            'updated': Config(),
            'abbreviation': Config(translated=True),
            'code': Config(),
            'name': Config(translated=True)
        }
    },
    'Department': {
        'model_class': Department,
        'resource_path': '/departments',
        'mapping': {
            'id': Config(primary=True),
            'updated': Config(),
            'abbreviation': Config(translated=True),
            'code': Config(),
            'name': Config(translated=True)
        }
    },
    'Council': {
        'model_class': Council,
        'resource_path': '/councils',
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
        'model_class': AffairTopic,
        'resource_path': '/affairs/topics',
        'mapping': {
            'id': Config(primary=True),
            'updated': Config(),
            'code': Config(),
            'name': Config(translated=True),
        }
    },
    'AffairType': {
        'model_class': AffairType,
        'resource_path': '/affairs/types',
        'mapping': {
            'id': Config(primary=True),
            'updated': Config(),
            'code': Config(),
            'name': Config(translated=True),
        }
    },
    'AffairState': {
        'model_class': AffairState,
        'resource_path': '/affairs/states',
        'mapping': {
            'id': Config(primary=True),
            'updated': Config(),
            'code': Config(),
            'sorting': Config(),
            'parent/id': Config(fk_type=AffairState, model_column_name='parent', null=True),
            'name': Config(translated=True),
        }
    },
    'LegislativePeriod': {
        'model_class': LegislativePeriod,
        'resource_path': '/legislativeperiods',
        'mapping': {
            'id': Config(primary=True),
            'updated': Config(),
            'code': Config(),
            'from': Config(model_column_name='from_date'),
            'name': Config(translated=True),
            'to': Config(model_column_name='to_date'),
        }
    }
}


class Command(BaseCommand):
    help = 'Import departments from parlament.ch'

    def add_arguments(self, parser):
        parser.add_argument('--models', nargs='+', help="Limit import to this models", type=str)
        parser.add_argument('--show-models', action='store_true', dest='list', default=False,
                            help='List available models')

    def handle(self, *args, **options):
        if options['list']:
            jobs = ", ".join(configurations)
            self.stdout.write("Available jobs:")
            for j in configurations:
                self.stdout.write(" - " + j)
            return

        if options['models']:
            unwanted = configurations.keys() - set(options['models'])
            for unwanted_key in unwanted: del configurations[unwanted_key]

        for model_name, config in configurations.items():
            self.stdout.write("Importing '{}' data ".format(model_name))
            for index, language in enumerate([x[0] for x in settings.LANGUAGES]):
                update_from_webservice(self, config, language, index == 0)
