from django.test import TestCase

from apps.curia_vista.models import Faction


class TestFaction(TestCase):
    def setUp(self):
        self.T = Faction(id=1, updated='2015-05-17T21:18:19Z', abbreviation='FOO', code='XYZ',
                         from_date='2015-05-17T21:18:19Z', to_date=None, name='foo bar', short_name='foo')

    def test___str__(self):
        self.assertEqual('foo bar', str(self.T))
