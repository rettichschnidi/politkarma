from django.test import TestCase

from apps.curia_vista.models import Vote


class TestFaction(TestCase):
    def setUp(self):
        self.T = Vote(id=1, updated='2015-05-17T21:18:19Z', title='a vote title', affair_votes=123)

    def test___str__(self):
        self.assertEqual('a vote title', str(self.T))
