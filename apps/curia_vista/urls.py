from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.conf.urls import url

from apps.curia_vista.models import Department

urlpatterns = [
    url(r'^department/$', ListView.as_view(context_object_name='departments',
                                           queryset=Department.objects.order_by('-name'))),
]
