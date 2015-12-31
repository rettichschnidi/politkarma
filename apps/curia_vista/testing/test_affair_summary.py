from django.test import TestCase

from apps.curia_vista.models import AffairSummary


class TestAffair(TestCase):
    def setUp(self):
        self.T = AffairSummary(id=1, updated='2015-05-17T21:18:19Z', formatted_id='16.203', title='test')

    def test___str__(self):
        self.assertEqual('test', str(self.T))
