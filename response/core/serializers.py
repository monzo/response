from rest_framework import serializers
from rest_framework.decorators import action

from response.core.models.incident import Incident
from response.core.models.action import Action
from response.core.models.user_external import ExternalUser

from django.contrib.auth.models import User


class ExternalUserSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = ExternalUser
        fields = ('app_id', 'external_id', 'owner', 'display_name')


class ActionSerializer(serializers.HyperlinkedModelSerializer):
    # Serializers define the API representation.
    incident = serializers.PrimaryKeyRelatedField(queryset=Incident.objects.all(), required=False)
    user = serializers.PrimaryKeyRelatedField(queryset=ExternalUser.objects.all(), required=False)

    class Meta:
        model = Action
        fields = ('pk', 'details', 'done', 'incident', 'user')


class IncidentSerializer(serializers.HyperlinkedModelSerializer):
    reporter = serializers.PrimaryKeyRelatedField(queryset=ExternalUser.objects.all(), required=False)
    lead = serializers.PrimaryKeyRelatedField(queryset=ExternalUser.objects.all(), required=False)

    class Meta:
        model = Incident
        fields = ('pk','report', 'reporter', 'lead', 'start_time', 'end_time', 'report_time', 'action_set')

    def __init__(self, *args, **kwargs):
        super(IncidentSerializer, self).__init__(*args, **kwargs)
        request = kwargs['context']['request']
        expand = request.GET.get('expand', "").split(',')

        if 'actions' in expand:
            self.fields['action_set'] = ActionSerializer(many=True, read_only=True)
