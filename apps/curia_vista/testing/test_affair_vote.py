from django.test import TestCase

from apps.curia_vista.models import AffairVote, Affair


class TestAffairVote(TestCase):
    def setUp(self):
        self.T = AffairVote(id=1, date='2015-05-17T21:18:19Z', division_text="text", meaning_no='no',
                            meaning_yes='yes', registration_number=123, submission_text='foobar',
                            affair=Affair(id=1, updated='2015-05-17T21:18:19Z', short_id="16.203"))

    def test___str__(self):
        self.assertEqual('text', str(self.T))
