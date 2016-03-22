import datetime
import random

from django.views.generic import TemplateView

from apps.curia_vista.models import *


# Create your views here.
class PartyView(TemplateView):
    template_name = 'curia_vista/party_list.html'

    def get(self, request, *args, **kwargs):
        context = {'parties': Party.objects.order_by('name')}
        return self.render_to_response(context)


class VoteView(TemplateView):
    template_name = 'curia_vista/vote_helper.html'
    html_date_format = "%Y-%m-%d"
    parameter_startdate = "startdate"
    parameter_enddate = "enddate"
    parameter_organizations = "organizations"
    parameter_cantons = "cantons"

    @staticmethod
    def councillor_to_result(councillor, rank_iterator):
        party = councillor.party
        party_name = None if party is None else party.name
        return KarmaResultRow(next(rank_iterator), councillor.full_name, party_name, random.randint(-1000, 1000))

    def get(self, request, *args, **kwargs):
        query_dict = VoteView.get_query_dict(request)
        print(query_dict)
        cantons = Canton.objects.order_by('name')
        first_av = next(iter(AffairVote.objects.order_by('-date')), None)
        start_date = query_dict.get(VoteView.parameter_startdate,
                                    "1970-01-01" if first_av is None else first_av.date.strftime(
                                        VoteView.html_date_format))
        end_date = query_dict.get(VoteView.parameter_enddate,
                                  datetime.datetime.now().strftime(VoteView.html_date_format))
        selected_organizations = query_dict.get(VoteView.parameter_organizations, [])
        selected_cantons = query_dict.get(VoteView.parameter_cantons, [])
        organizations = Organization.objects.order_by('name')

        rank_iterator = iter(range(1, 100))
        karma_ranking = [VoteView.councillor_to_result(c, rank_iterator) for c in Councillor.objects.all()[0:10]]
        karma_ranking.sort(key=lambda a: a.rank)

        context = {
            'ranking': karma_ranking,
            'organizations': organizations,
            'cantons': cantons,
            'selected_cantons': selected_cantons,
            'selected_organizations': selected_organizations,
            VoteView.parameter_startdate: start_date,
            VoteView.parameter_enddate: end_date,
        }
        return self.render_to_response(context)

    @staticmethod
    def get_query_dict(request):
        if request.method == 'GET':
            return request.GET
        if request.method == 'PUT':
            return request.PUT
        return {}


class KarmaResultRow:
    def __init__(self, rank, name, party, score):
        self.rank = rank
        self.name = name
        self.party = party
        self.score = score
