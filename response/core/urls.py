from django.conf.urls import url, include
from rest_framework import routers

from response.core.views import IncidentViewSet, ActionViewSet, ExternalUserViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'incidents', IncidentViewSet, base_name='Incidents')
router.register(r'actions', ActionViewSet)
router.register(r'ExternalUser', ExternalUserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
]
