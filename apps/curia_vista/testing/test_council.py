from django.test import TestCase

from apps.curia_vista.models import Council


class TestCouncil(TestCase):
    def setUp(self):
        self.T = Council(id=1, updated='2010-12-26T13:07:49Z', code='RAT_1_', type='N')

    def test___str__(self):
        self.assertEqual('Nationalrat', self.T.name)

    def test_abbreviation(self):
        self.assertEqual('NR', self.T.abbreviation)

    def test_validate(self):
        self.T.full_clean()

    def test_invalid_code(self):
        self.T.code = 'RAT_666_'
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            if self.T.full_clean():
                self.fail('Invalid code may not be validated')