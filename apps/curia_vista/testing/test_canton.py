from unittest import TestCase

from apps.curia_vista.models import Canton


class TestCanton(TestCase):
    def setUp(self):
        self.T = Canton(id=14, updated='2010-12-26T13:05:26Z', code='KAN_14_')

    def test_abbreviation(self):
        self.assertEqual('SH', self.T.abbreviation)

    def test___str__(self):
        self.assertEqual('Schaffhausen', str(self.T))

    def test_validate(self):
        self.T.full_clean()

    def test_validate_faulty_code(self):
        self.T.code = 'KAN_666_'
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            if self.T.full_clean():
                self.fail('Invalid code may not be validated')

