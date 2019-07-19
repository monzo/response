from rest_framework import viewsets

from response.core.models.incident import Incident
from response.core.models.action import Action
from response.core.models.user_external import ExternalUser
from response.core.serializers import ExternalUserSerializer, ActionSerializer, IncidentSerializer

from datetime import datetime
from calendar import monthrange


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
    pagination_class = None  # Remove pagination

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
