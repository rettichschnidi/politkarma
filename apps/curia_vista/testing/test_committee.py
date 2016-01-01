from django.test import TestCase

from apps.curia_vista.models import Committee


class TestFaction(TestCase):
    def setUp(self):
        self.T = Committee(id=1, updated='2010-12-26T13:06:13Z', abbreviation='Bü-NR', code='KOM_1_',
                           committee_number='1', from_date='1848-11-07T00:00:00Z', is_active=True, name='Büro NR',
                           type_code='1')

    def test___str__(self):
        self.assertEqual('Büro NR', str(self.T))
