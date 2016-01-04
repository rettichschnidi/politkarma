from django.conf.urls import url
from django.views.generic.list import ListView

from apps.curia_vista.models import Department
from apps.curia_vista.views import *

urlpatterns = [
    url(r'^department/$', ListView.as_view(context_object_name='departments',
                                           queryset=Department.objects.order_by('-name'))),
    url(r'^party/$', PartyView.as_view(), name='party'),
]
