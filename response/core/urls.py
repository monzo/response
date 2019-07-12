from django.conf.urls import url, include
from rest_framework import routers, viewsets, pagination
from rest_framework.decorators import action

from response.core.models.incident import Incident
from response.core.models.action import Action
from response.core.models.user_external import ExternalUser

from datetime import datetime
from calendar import monthrange

from response.core.serializers import *

class ExternalUserViewSet(viewsets.ModelViewSet):
    # ViewSets define the view behavior.
    queryset = ExternalUser.objects.all()
    serializer_class = ExternalUserSerializer


class ActionViewSet(viewsets.ModelViewSet):
    # ViewSets define the view behavior.
    queryset = Action.objects.all()
    serializer_class = ActionSerializer


# Will return the incidents of the current month
# Can pass ?start=2019-05-28&end=2019-06-03 to change range
class IncidentViewSet(viewsets.ModelViewSet):
    # ViewSets define the view behavior.

    serializer_class = IncidentSerializer
    pagination_class = None # Remove pagination

    def get_queryset(self):
        # Same query is used to get single items so we check if pk is passed
        # incident/2/ if we use the filter below we would have to have correct time range
        if 'pk' in self.kwargs:
            return Incident.objects.filter(pk=self.kwargs['pk'])

        today = datetime.today()
        first_day_of_current_month = datetime(today.year, today.month, 1)
        days_in_month = monthrange(today.year, today.month)[1]
        last_day_of_current_month = datetime(today.year, today.month, days_in_month)

        start = self.request.GET.get('start', first_day_of_current_month)
        end = self.request.GET.get('end', last_day_of_current_month)

        return Incident.objects.filter(start_time__gte=start, start_time__lte=end)

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'incidents', IncidentViewSet, base_name='Incidents')
router.register(r'actions', ActionViewSet)
router.register(r'ExternalUser', ExternalUserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
