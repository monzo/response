from datetime import datetime, timedelta

from rest_framework import pagination, viewsets

from response.core import serializers
from response.core.models.action import Action
from response.core.models.event import Event
from response.core.models.incident import Incident
from response.core.models.timeline import TimelineEvent
from response.core.models.user_external import ExternalUser
from response.core.util import LargeResultsSetPagination


class ExternalUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExternalUser.objects.all()
    serializer_class = serializers.ExternalUserSerializer
    # Set page size to 1000
    pagination_class = LargeResultsSetPagination


class ActionViewSet(viewsets.ModelViewSet):
    # ViewSets define the view behavior.
    queryset = Action.objects.all()
    serializer_class = serializers.ActionSerializer


class IncidentViewSet(viewsets.ModelViewSet):
    """
    Allows getting a list of Incidents (sorted by report time from newest to
    oldest), and updating existing ones.

    Note that Incidents can only be created via the Slack workflow.
    """

    queryset = Incident.objects.order_by("-report_time")

    serializer_class = serializers.IncidentSerializer
    pagination_class = pagination.LimitOffsetPagination


class IncidentActionViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ActionSerializer

    def get_queryset(self):
        incident_pk = self.kwargs["incident_pk"]
        return Action.objects.filter(incident_id=incident_pk)

    def perform_create(self, serializer):
        incident_pk = self.kwargs["incident_pk"]
        serializer.save(incident_id=incident_pk)


class IncidentsByMonthViewSet(viewsets.ModelViewSet):
    """
    Allows getting a list of Incidents for a given year/month (sorted by
    report time from newest to oldest), and updating existing ones.

    Note that Incidents can only be created via the Slack workflow.
    """

    queryset = Incident.objects.order_by("-report_time")

    serializer_class = serializers.IncidentSerializer
    pagination_class = pagination.LimitOffsetPagination

    def list(self, request, year, month):
        incidents = self.queryset.filter(
            report_time__year=year, report_time__month=month
        )
        page = self.paginate_queryset(incidents)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)


class IncidentTimelineEventViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.TimelineEventSerializer

    def get_queryset(self):
        incident_pk = self.kwargs["incident_pk"]
        return TimelineEvent.objects.filter(incident_id=incident_pk)

    def perform_create(self, serializer):
        incident_pk = self.kwargs["incident_pk"]
        serializer.save(incident_id=incident_pk)


class EventsViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = serializers.EventSerializer

    def get_queryset(self):
        from_ts = self.request.query_params.get(
            "from", datetime.now(tz=None) - timedelta(days=1)
        )
        to_ts = self.request.query_params.get("to", datetime.now(tz=None))
        return Event.objects.filter(timestamp__range=(from_ts, to_ts))
