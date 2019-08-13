from rest_framework import pagination, viewsets

from response.core.models.incident import Incident
from response.core.models.action import Action
from response.core.models.user_external import ExternalUser
from response.core import serializers

from datetime import datetime
from calendar import monthrange


class ExternalUserViewSet(viewsets.ModelViewSet):
    # ViewSets define the view behavior.
    queryset = ExternalUser.objects.all()
    serializer_class = serializers.ExternalUserSerializer


class ActionViewSet(viewsets.ModelViewSet):
    # ViewSets define the view behavior.
    queryset = Action.objects.all()
    serializer_class = serializers.ActionSerializer


class IncidentViewSet(viewsets.ModelViewSet):
    # ViewSets define the view behavior.

    queryset = Incident.objects.order_by("-report_time")

    serializer_class = serializers.IncidentSerializer
    pagination_class = pagination.LimitOffsetPagination
