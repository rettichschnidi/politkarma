from django.test import TestCase
from mixer.backend.django import mixer
from django.contrib.auth.models import User

from apps.brahman.models import Organisation


class TestOrganisation(TestCase):
    def setUp(self):
        self.User = mixer.blend(User, first_name="FirstName", last_name="LastName")
        self.T = mixer.blend(Organisation, user=self.User)

    def test___str__(self):
        self.assertEqual("FirstName LastName", str(self.T))
