from django.test import TestCase

from apps.curia_vista.models import Councillor


class TestCouncillor(TestCase):
    def setUp(self):
        self.T = Councillor(id=1, updated='2015-05-17T21:18:19Z', active=False, first_name='Giuseppe',
                            last_name='a Marca', official_denomination=None, salutation_letter=None,
                            salutation_title=None)

    def test___str__(self):
        self.assertEqual('a Marca Giuseppe', str(self.T))
