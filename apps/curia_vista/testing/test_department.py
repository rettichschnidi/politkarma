from django.test import TestCase

from apps.curia_vista.models import Department


class TestDepartment(TestCase):
    def setUp(self):
        self.T = Department(id=1, updated='2010-12-26T13:05:26Z', code='DEP_1_')

    def test_name(self):
        self.assertEqual('Parlament', self.T.name)

    def test___str__(self):
        self.assertEqual('Parl', str(self.T))

    def test_validate(self):
        self.T.full_clean()

    def test_validate_faulty_code(self):
        self.T.code = 'DEP_666_'
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            if self.T.full_clean():
                self.fail('Invalid code may not be validated')
