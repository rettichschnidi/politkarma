from django.test import TestCase

from apps.curia_vista.models import Committee, Council


class TestFaction(TestCase):
    def setUp(self):
        self.council = Council(id=1, updated='2010-12-26T13:07:49Z', abbreviation='NR', code='RAT_1_', type='N',
                               name='Nationalrat')
        self.committee = Committee(id=1, updated='2010-12-26T13:06:13Z', abbreviation='Bü-NR', code='KOM_1_', number=1,
                                   council=self.council, from_date='1848-11-07T00:00:00Z', is_active=True,
                                   name='Büro NR', type_code='1')
        self.T = self.committee

    def test___str__(self):
        self.assertEqual('Büro NR', str(self.T))
