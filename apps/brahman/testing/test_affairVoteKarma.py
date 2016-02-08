from django.test import TestCase
from mixer.backend.django import mixer
from apps.brahman.models import AffairVoteKarma


class TestAffairVoteKarma(TestCase):
    def setUp(self):
        self.T = mixer.blend(AffairVoteKarma, vote_decision='Y', karma=-1)

    def test___str__(self):
        self.assertEqual("Y: -1", str(self.T))
