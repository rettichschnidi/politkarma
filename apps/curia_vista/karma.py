import random

from apps.curia_vista.models import *


class KarmaCalculator:
    @staticmethod
    def councillor_to_result(councillor, rank_iterator):
        party = councillor.party
        party_name = None if party is None else party.name
        return KarmaResultRow(next(rank_iterator), councillor.full_name, party_name, random.randint(-1000, 1000))

    @staticmethod
    def get_top_karma_scores(start_date, end_date, cantons, organizations, top_n):
        # TODO: implement...
        rank_iterator = iter(range(1, top_n + 1))
        karma_ranking = [KarmaCalculator.councillor_to_result(c, rank_iterator) for c in
                         Councillor.objects.all()[0:top_n]]
        karma_ranking.sort(key=lambda a: a.rank)
        return karma_ranking


class KarmaResultRow:
    def __init__(self, rank, name, party, score):
        self.rank = rank
        self.name = name
        self.party = party
        self.score = score
