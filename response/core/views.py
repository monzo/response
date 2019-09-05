from rest_framework import pagination, viewsets

from response.core import serializers
from response.core.models.action import Action
from response.core.models.incident import Incident
from response.core.models.timeline import TimelineEvent
from response.core.models.user_external import ExternalUser


class ExternalUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExternalUser.objects.all()
    serializer_class = serializers.ExternalUserSerializer


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
