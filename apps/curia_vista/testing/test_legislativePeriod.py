from unittest import TestCase

from apps.curia_vista.models import LegislativePeriod


class TestLegislativePeriod(TestCase):
    def setUp(self):
        self.T = LegislativePeriod(id=50,
                                   updated='2014-05-27T15:53:59Z',
                                   code=50,
                                   from_date='2015-11-30T00:00:00Z',
                                   name='50. Legislatur',
                                   to_date='2019-11-29T00:00:00Z')

    def test___str__(self):
        self.assertEqual('50. Legislatur', str(self.T))
