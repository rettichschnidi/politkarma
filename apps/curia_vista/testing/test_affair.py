from django.test import TestCase

from apps.curia_vista.models import Affair


class TestAffair(TestCase):
    def setUp(self):
        self.T = Affair(id=1, updated='2015-05-17T21:18:19Z', short_id="16.203")

    def test___str__(self):
        self.assertEqual('16.203', str(self.T))
