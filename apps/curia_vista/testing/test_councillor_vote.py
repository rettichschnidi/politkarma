from django.test import TestCase

from apps.curia_vista.models import Councillor, CouncillorVote, Affair, AffairVote


class TestAffairVote(TestCase):
    def setUp(self):
        councillor = Councillor(id=1, updated='2015-05-17T21:18:19Z', active=False, first_name='Giuseppe',
                                last_name='a Marca', official_denomination=None, salutation_letter=None,
                                salutation_title=None)
        affair_vote = AffairVote(id=1, date='2015-05-17T21:18:19Z', division_text="text", meaning_no='no',
                                 meaning_yes='yes', registration_number=123, submission_text='foobar',
                                 affair=Affair(id=1, updated='2015-05-17T21:18:19Z', short_id="16.203"))
        self.T = CouncillorVote(id=1, decision='Yes', councillor=councillor, affair_vote=affair_vote)

    def test___str__(self):
        self.assertEqual('Yes', str(self.T))
