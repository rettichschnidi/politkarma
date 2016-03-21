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

    def get(self, request, *args, **kwargs):
        context = {'cantons': Canton.objects.order_by('name')}
        return self.render_to_response(context)
