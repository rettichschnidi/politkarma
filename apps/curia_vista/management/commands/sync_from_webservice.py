from django.core.management.base import BaseCommand

from apps.curia_vista.management.utils import Config, update_from_webservice
from politkarma import settings

import apps.curia_vista.models

configurations = [
    {
        'name': 'Canton',
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
    {
        'name': 'Department',
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
    {
        'name': 'Council',
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
    {
        'name': 'AffairTopic',
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
    {
        'name': 'AffairType',
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
    {
        'name': 'AffairState',
        'model_class': apps.curia_vista.models.AffairState,
        'resource_path': '/affairs/states',
        'has_more': False,
        'mapping': {
            'id': Config(primary=True),
            'updated': Config(),
            'code': Config(),
            'sorting': Config(),
            'parent': Config(fk_type=apps.curia_vista.models.AffairState, model_column_name='parent', null=True,
                             sub_keys=['id']),
            'name': Config(translated=True),
        }
    },
    {
        'name': 'LegislativePeriod',
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
    {
        'name': 'Affair',
        'model_class': apps.curia_vista.models.Affair,
        'resource_path': '/affairs',
        'has_more': True,
        'mapping': {
            'id': Config(primary=True),
            'updated': Config(),
            'shortId': Config(model_column_name='short_id'),
        }
    },
    {
        'name': 'Session',
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
    },
    {
        'name': 'Party',
        'model_class': apps.curia_vista.models.Party,
        'resource_path': '/parties/historic',
        'has_more': True,
        'mapping': {
            'id': Config(primary=True),
            'updated': Config(),
            'abbreviation': Config(translated=True),
            'code': Config(),
            'name': Config(translated=True),
        }
    },
    {
        'name': 'Faction',
        'model_class': apps.curia_vista.models.Faction,
        'resource_path': '/factions/historic',
        'has_more': True,
        'mapping': {
            'id': Config(primary=True, model_column_name='the_id'),
            'updated': Config(),
            'abbreviation': Config(translated=True),
            'code': Config(),
            'from': Config(primary=True, model_column_name='from_date'),
            'name': Config(translated=True),
            'to': Config(model_column_name='to_date', null=True),
            'shortName': Config(model_column_name='short_name', translated=True)
        }
    },
    {
        'name': 'Councillor',
        'model_class': apps.curia_vista.models.Councillor,
        'resource_path': '/councillors',
        'has_more': True,
        'mapping': {
            'id': Config(primary=True),
            'updated': Config(),
            'active': Config(),
            'code': Config(),
            'firstName': Config(model_column_name='first_name'),
            'lastName': Config(model_column_name='last_name'),
            'number': Config(null=True),
            'officialDenomination': Config(model_column_name='official_denomination'),
            'salutationLetter': Config(model_column_name='salutation_letter'),
            'salutationTitle': Config(model_column_name='salutation_title'),
        }
    },
    {
        'name': 'CouncillorBasicDetails',
        'model_class': apps.curia_vista.models.Councillor,
        'resource_path': '/councillors/basicdetails',
        'has_more': True,
        'is_update': True,
        'mapping': {
            'id': Config(primary=True),
            'biographyUrl': Config(model_column_name='biography_url', translated=True),
            'pictureUrl': Config(model_column_name='picture_url'),
        }
    },
    {
        'name': 'Committee',
        'model_class': apps.curia_vista.models.Committee,
        'resource_path': '/committees',
        'has_more': True,
        'mapping': {
            'id': Config(primary=True),
            'updated': Config(),
            'abbreviation': Config(translated=True),
            'code': Config(),
            'committeeNumber': Config(model_column_name='number'),
            'council': Config(fk_type=apps.curia_vista.models.Council, model_column_name='council', sub_keys=['id']),
            'from': Config(model_column_name='from_date'),
            'isActive': Config(model_column_name='is_active', default=False, null=True),
            'name': Config(translated=True),
            'subcommitteeNumber': Config(model_column_name='sub_number', null=True),
            'to': Config(model_column_name='to_date', null=True),
            'typeCode': Config(model_column_name='type_code'),
        }
    },
    {
        'name': 'AffairSummary',
        'model_class': apps.curia_vista.models.AffairSummary,
        'resource_path': '/affairsummaries',
        'has_more': True,
        'mapping': {
            'id': Config(primary=True),
            'updated': Config(),
            'formattedId': Config(model_column_name='formatted_id'),
            'title': Config(translated=True),
        }
    }
]


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
            jobs = ", ".join([x['name'] for x in configurations])
            self.stdout.write("Available jobs:")
            for j in configurations:
                self.stdout.write(" - " + j['name'])
            return

        if options['models']:
            configurations[:] = [x for x in configurations if x['name'] in options['models']]

        for config in configurations:
            self.stdout.write("Updating data for model '{}'".format(config['name']))
            if options['main_only']:
                update_from_webservice(self, config, Command.languages[0], False)
            else:
                for index, language in enumerate(Command.languages):
                    is_update = 'is_update' in config and config['is_update']
                    update_from_webservice(self, config, language, index != 0 or is_update)
