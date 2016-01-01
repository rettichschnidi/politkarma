from django.test import TestCase

from apps.curia_vista.models import Council


class TestCouncil(TestCase):
    def setUp(self):
        self.T = Council(id=1, updated='2010-12-26T13:07:49Z', abbreviation='NR', code='RAT_1_', type='N',
                         name='Nationalrat')
        self.T.save()

    def test___str__(self):
        self.assertEqual('Nationalrat', str(self.T))

    def test_name_translation(self):
        from django.utils import translation
        translation.activate('fr')
        T, created = Council.objects.update_or_create(id=1, updated='2010-12-26T13:07:49Z', code='RAT_1_', type='N',
                                                      defaults={'abbreviation': 'CN', 'name': 'Conseil national'})
        self.assertFalse(created)
        self.assertEqual('Conseil national', T.name)
        translation.activate('de')
        self.assertEqual('Nationalrat', T.name)
