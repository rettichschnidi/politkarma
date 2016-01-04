from django.views.generic import TemplateView

from apps.curia_vista.models import Party


# Create your views here.
class PartyView(TemplateView):
    template_name = 'curia_vista/party_list.html'

    def get(self, request, *args, **kwargs):
        context = {'parties': Party.objects.order_by('name')}
        return self.render_to_response(context)
