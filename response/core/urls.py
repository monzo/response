from django.conf.urls import include, url
from rest_framework import routers

from response.core.views import (
    ActionViewSet,
    EventsViewSet,
    ExternalUserViewSet,
    IncidentActionViewSet,
    IncidentsByMonthViewSet,
    IncidentTimelineEventViewSet,
    IncidentViewSet,
)

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r"incidents", IncidentViewSet, basename="incident")
router.register(
    r"incidents/(?P<incident_pk>[0-9]+)/actions",
    IncidentActionViewSet,
    basename="incident-action",
)
router.register(
    r"incidents/bymonth/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})",
    IncidentsByMonthViewSet,
    basename="incidents-bymonth",
)
router.register(
    r"incidents/(?P<incident_pk>[0-9]+)/timeline/events",
    IncidentTimelineEventViewSet,
    basename="incident-timeline-event",
)
router.register(r"actions", ActionViewSet)
router.register(r"users", ExternalUserViewSet)
router.register(r"events", EventsViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [url(r"^", include(router.urls))]
