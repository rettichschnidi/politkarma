from django.core.management.base import BaseCommand

from apps.curia_vista.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        KarmaRule.objects.all().delete()

        bc = Organization.objects.get(name="Beispiel Club")
        for vote in AffairVote.objects.filter(submission_text__icontains="europa"):
            print("Beispiel Club insert")
            KarmaRule.objects.create(description="generated entry", organization=bc,
                                     affair_vote=vote, expected_decision="Yes", karma_multiplier=1)

        kf = Organization.objects.get(name="Katzenfreunde")
        for vote in AffairVote.objects.filter(submission_text__icontains="gesetz"):
            print("Katzenfreunde insert")
            KarmaRule.objects.create(description="generated entry", organization=kf,
                                     affair_vote=vote, expected_decision="No", karma_multiplier=1)

        hv = Organization.objects.get(name="Hundezüchter Verein")
        for vote in AffairVote.objects.filter(submission_text__icontains="steuer"):
            print("Hundezüchter Verein")
            KarmaRule.objects.create(description="generated entry", organization=hv,
                                     affair_vote=vote, expected_decision="Yes", karma_multiplier=1)
