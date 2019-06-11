from django.conf.urls import url, include
from rest_framework import routers, serializers, viewsets, pagination
from rest_framework.response import Response
from rest_framework.decorators import action

from core.models.incident import Incident
from core.models.action import Action

from slack.models import SlackUser
from django.contrib.auth.models import User

from datetime import datetime, date
import calendar


class SlackUserSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = SlackUser
        fields = ('user_id', 'owner')

class SlackUserViewSet(viewsets.ModelViewSet):
    # ViewSets define the view behavior.
    queryset = SlackUser.objects.all()
    serializer_class = SlackUserSerializer

class ActionSerializer(serializers.HyperlinkedModelSerializer):
    # Serializers define the API representation.
    incident = serializers.PrimaryKeyRelatedField(queryset=Incident.objects.all(), required=False)
    user = serializers.PrimaryKeyRelatedField(queryset=SlackUser.objects.all(), required=False)

    class Meta:
        model = Action
        fields = ('pk', 'details', 'done', 'incident', 'user')

class ActionViewSet(viewsets.ModelViewSet):
    # ViewSets define the view behavior.
    queryset = Action.objects.all()
    serializer_class = ActionSerializer


class IncidentSerializer(serializers.HyperlinkedModelSerializer):
    reporter = serializers.PrimaryKeyRelatedField(queryset=SlackUser.objects.all(), required=False)
    lead = serializers.PrimaryKeyRelatedField(queryset=SlackUser.objects.all(), required=False)

    class Meta:
        model = Incident
        fields = ('pk','report', 'reporter', 'lead', 'start_time', 'end_time', 'report_time', 'action_set')

    def __init__(self, *args, **kwargs):
        super(IncidentSerializer, self).__init__(*args, **kwargs)
        request = kwargs['context']['request']
        expand = request.GET.get('expand', "").split(',')

        if 'actions' in expand:
            self.fields['action_set'] = ActionSerializer(many=True, read_only=True)


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
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        last_day_of_current_month = datetime(today.year, today.month, days_in_month)

        start = self.request.GET.get('start', first_day_of_current_month)
        end = self.request.GET.get('end', last_day_of_current_month)

        return Incident.objects.filter(start_time__gte=start, start_time__lte=end)

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'incidents', IncidentViewSet, base_name='Incidents')
router.register(r'actions', ActionViewSet)
router.register(r'slack_users', SlackUserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
