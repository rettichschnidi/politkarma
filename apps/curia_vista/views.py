import datetime

from django import forms
from django.db.models import Min, Max
from django.views.generic import TemplateView

from apps.curia_vista.karma import *


# Create your views here.
class PartyView(TemplateView):
    template_name = 'curia_vista/party_list.html'

    def get(self, request, *args, **kwargs):
        context = {'parties': Party.objects.order_by('name')}
        return self.render_to_response(context)


class VoteForm(forms.Form):
    date_span = AffairVote.objects.aggregate(Min('date'), Max('date'))
    years_to_display = range(
        (datetime.date(1970, 1, 1) if date_span['date__min'] is None else date_span['date__min']).year,
        (datetime.datetime.now() if date_span['date__max'] is None else date_span['date__max']).year)

    start_date = forms.DateField(label="Start date",
                                 widget=forms.SelectDateWidget(attrs={'id': 'start_date'}, years=years_to_display))
    end_date = forms.DateField(label="End date",
                               widget=forms.SelectDateWidget(attrs={'id': 'end_date'}, years=years_to_display))
    cantons = forms.ModelMultipleChoiceField(queryset=Canton.objects.order_by('name'), to_field_name="name",
                                             label="Cantons",
                                             widget=forms.SelectMultiple(attrs={'id': 'cantons'}))
    organizations = forms.ModelMultipleChoiceField(queryset=Organization.objects.order_by('name'), to_field_name="name",
                                                   label="Organizations",
                                                   widget=forms.SelectMultiple(attrs={'id': 'organizations'}))


class KarmaResult:
    ranking = ()
    cantons = ()
    organizations = ()
    start_date = None
    end_date = None
    import_date = "1970-01-01"


class VoteView(TemplateView):
    template_name = 'curia_vista/vote_helper.html'

    def get(self, request, *args, **kwargs):
        form = VoteForm(self.get_query_dict(request))
        karma_result = None
        if form.is_valid():
            karma_result = KarmaResult()
            karma_result.start_date = form.cleaned_data['start_date']
            karma_result.end_date = form.cleaned_data['end_date']
            karma_result.cantons = list(map(lambda c: c.name, form.cleaned_data['cantons']))
            karma_result.organizations = list(map(lambda o: o.name, form.cleaned_data['organizations']))
            karma_result.ranking = KarmaCalculator.get_top_karma_scores(form.cleaned_data['start_date'],
                                                                        form.cleaned_data['end_date'],
                                                                        form.cleaned_data['cantons'],
                                                                        form.cleaned_data['organizations'],
                                                                        10)

        else:
            print("don't like form: {}".format(form.errors))

        context = {
            'form': form,
            'result': karma_result,
        }
        return self.render_to_response(context)

    @staticmethod
    def get_query_dict(request):
        if request.method == 'GET':
            return request.GET
        if request.method == 'PUT':
            return request.PUT
        return {}
