import logging
import random

# from django.db.models import Q

from apps.curia_vista.models import *

logging.getLogger().setLevel(logging.DEBUG)


class KarmaCalculator:
    organization_placeholder = "__organizations__"
    canton_placeholder = "__cantons__"
    karma_query = (
    "select councillor_id, sum(case when kr.expected_decision = cv.decision then 1 else -1 end * kr.karma_multiplier) as karma_change "
    "from curia_vista_karmarule kr inner join curia_vista_affairvote av on (av.id = kr.affair_vote_id) inner join curia_vista_councillorvote cv on (cv.affair_vote_id = av.id) "
    "where av.date BETWEEN date(%s) AND date(%s) AND kr.organization_id in (" + organization_placeholder + ") "
                                                                                                           "group by councillor_id "
                                                                                                           "order by 2 desc ")

    @staticmethod
    def councillor_to_result(councillor, rank_iterator):
        party = councillor.party
        party_name = None if party is None else party.name
        return KarmaResultRow(next(rank_iterator), councillor.full_name, party_name, random.randint(-1000, 1000))

    @staticmethod
    def get_top_karma_scores(start_date, end_date, cantons, organizations, top_n):
        # TODO: implement...
        # reduce(operator.and_, (Q(organization=organization) for organization in organizations))
        # filter_args = (Q(organization__in=organizations) & Q(affair_vote__date__range=[start_date, end_date]))
        # print("{}".format(filter_args))
        # rules = KarmaRule.objects.filter(filter_args)
        # for rule in rules:
        #    print("---{}".format(rule))

        councillor_index = {x.id: x for x in Councillor.objects.all()}

        from django.db import connection
        cursor = connection.cursor()
        organization_variables = ",".join(map(lambda x: '%s', organizations))
        organization_ids = list(map(lambda x: x.id, organizations))
        canton_variables = ",".join(map(lambda x: '%s', cantons))
        canton_ids = list(map(lambda x: x.id, cantons))

        query = KarmaCalculator.karma_query.replace(KarmaCalculator.canton_placeholder, canton_variables)
        query = query.replace(KarmaCalculator.organization_placeholder, organization_variables)
        parameters = [start_date.isoformat(), end_date.isoformat()] + organization_ids
        logging.debug("generated karma query: %s parameters: %s", query, parameters)
        cursor.execute(query, parameters)

        result = []
        rank = 0
        for row in cursor.fetchall():
            rank += 1
            councillor = councillor_index[row[0]]
            party = councillor.party
            party_name = None if party is None else party.name
            result.append(KarmaResultRow(rank, councillor.full_name, party_name, row[1]))

        # rank_iterator = iter(range(1, top_n + 1))
        # karma_ranking = [KarmaCalculator.councillor_to_result(c, rank_iterator) for c in
        #                 Councillor.objects.all()[0:top_n]]
        # karma_ranking.sort(key=lambda a: a.rank)
        return result


class KarmaResultRow:
    def __init__(self, rank, name, party, score):
        self.rank = rank
        self.name = name
        self.party = party
        self.score = score
