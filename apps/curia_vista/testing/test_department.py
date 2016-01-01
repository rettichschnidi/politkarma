from django.test import TestCase

from apps.curia_vista.models import Department


class TestDepartment(TestCase):
    def setUp(self):
        self.T = Department(id=1, updated='2010-12-26T13:05:26Z', abbreviation='Parl', code='DEP_1_',
                            name='Parlament')

    def test___str__(self):
        self.assertEqual('Parl', str(self.T))
