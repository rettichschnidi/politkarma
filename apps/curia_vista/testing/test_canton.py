from unittest import TestCase

from apps.curia_vista.models import Canton


class TestCanton(TestCase):
    def setUp(self):
        self.T = Canton(id=14, updated='2010-12-26T13:05:26Z', abbreviation='SH', code='KAN_14_', name='Schaffhausen')

    def test___str__(self):
        self.assertEqual('Schaffhausen', str(self.T))
