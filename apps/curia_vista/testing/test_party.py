from django.test import TestCase

from apps.curia_vista.models import Party


class TestFaction(TestCase):
    def setUp(self):
        self.T = Party(id=1, updated='2015-05-17T21:18:19Z', abbreviation='FOO', name='test party', code='fo')

    def test___str__(self):
        self.assertEqual('test party', str(self.T))
