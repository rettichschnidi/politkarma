from django.test import TestCase
from mixer.backend.django import mixer
from apps.brahman.models import RankedAffairVote


class TestRankedAffairVote(TestCase):
    def setUp(self):
        self.T = mixer.blend(RankedAffairVote)

    def test___str__(self):
        self.T.organisation.user.first_name = "FirstName"
        self.T.affair_vote.affair.title = "Example Affair Title"
        self.assertEqual("FirstName: 'Example Affair Title'", str(self.T))
