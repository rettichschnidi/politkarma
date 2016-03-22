from django.core.management.base import BaseCommand

from apps.curia_vista.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        Organization.objects.all().delete()
        Organization.objects.create(name="Beispiel Club", description="palceholder",
                                    logo_location="https://upload.wikimedia.org/wikipedia/commons/7/70/Example.png")
        Organization.objects.create(name="Katzenfreunde", description="placeholder",
                                    logo_location="http://placekitten.com/180/200")
        Organization.objects.create(name="Hundezüchter Verein", description="placeholder",
                                    logo_location="https://upload.wikimedia.org/wikipedia/commons/2/2d/Littlebluedog.svg")
