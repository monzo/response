from django.conf.urls import url, include
from rest_framework import routers, serializers, viewsets

from core.models.incident import Incident


class IncidentSerializer(serializers.HyperlinkedModelSerializer):
    # Serializers define the API representation.
    class Meta:
        model = Incident
        fields = ('report', 'reporter', 'report_time')


class IncidentViewSet(viewsets.ModelViewSet):
    # ViewSets define the view behavior.
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'incidents', IncidentViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
