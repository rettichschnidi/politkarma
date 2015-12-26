from django.test import TestCase

from apps.curia_vista.models import Council


class TestCouncil(TestCase):
    def setUp(self):
        self.T = Council(id=1, updated='2010-12-26T13:07:49Z', code='RAT_1_', type='N')

    def test___str__(self):
        self.assertEqual('Nationalrat', self.T.name)

    def test_abbreviation(self):
        self.assertEqual('NR', self.T.abbreviation)

