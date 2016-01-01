from django.core.management.base import BaseCommand
from apps.curia_vista.management.commands.update_affairs import Command as ImportCommandAffairs
from apps.curia_vista.management.commands.update_affair_summaries import Command as ImportCommandAffairSummaries
from apps.curia_vista.management.commands.update_cantons import Command as ImportCommandCanton
from apps.curia_vista.management.commands.update_councils import Command as ImportCommandCouncils
from apps.curia_vista.management.commands.update_councillors import Command as ImportCommandCouncillors
from apps.curia_vista.management.commands.update_departments import Command as ImportCommandDepartments
from apps.curia_vista.management.commands.update_factions import Command as ImportCommandFactions
from apps.curia_vista.management.commands.update_legislativePeriods import Command as ImportCommandLegislativePeriods
from apps.curia_vista.management.commands.update_parties import Command as ImportCommandParties
from apps.curia_vista.management.commands.update_sessions import Command as ImportCommandSessions
from apps.curia_vista.management.commands.update_committee import Command as ImportCommandCommittee


class Command(BaseCommand):
    help = 'Import/update all data from parlament.ch'
    commands = [
        ImportCommandAffairs,
        ImportCommandAffairSummaries,
        ImportCommandCanton,
        ImportCommandCouncils,
        ImportCommandCommittee,
        ImportCommandCouncillors,
        ImportCommandDepartments,
        ImportCommandFactions,
        ImportCommandLegislativePeriods,
        ImportCommandParties,
        ImportCommandSessions
    ]

    def handle(self, *args, **options):
        for cmd_class in Command.commands:
            cmd_class().handle(args, options)
