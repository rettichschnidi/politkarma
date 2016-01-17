from timeit import default_timer as timer

from django.core.management.base import BaseCommand

from apps.curia_vista.management.commands.update_affair_summaries import Command as ImportCommandAffairSummaries

from apps.curia_vista.management.commands.update_committee import Command as ImportCommandCommittee
from apps.curia_vista.management.commands.update_councillors import Command as ImportCommandCouncillors
from apps.curia_vista.management.commands.update_factions import Command as ImportCommandFactions


class Command(BaseCommand):
    help = 'Import/update all data from parlament.ch'
    commands = [
        ImportCommandAffairSummaries,
        ImportCommandCommittee,
        ImportCommandCouncillors,
        ImportCommandFactions,
    ]

    def handle(self, *args, **options):
        for cmd_class in Command.commands:
            start = timer()
            cmd_class().handle(args, options)
            self.stdout.write("Command '{0}' has been executed with arguments '{1}' and options '{2}'. Duration: {3}s"
                              .format(cmd_class, args, options, timer() - start))
