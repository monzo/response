from response.core.models import Action
from response.slack.models import CommsChannel, ExternalUser, Incident

from rest_framework import serializers


class ExternalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalUser
        fields = ("app_id", "external_id", "display_name")


class ActionSerializer(serializers.ModelSerializer):
    # Serializers define the API representation.
    incident = serializers.PrimaryKeyRelatedField(
        queryset=Incident.objects.all(), required=False
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=ExternalUser.objects.all(), required=False
    )

    class Meta:
        model = Action
        fields = ("pk", "details", "done", "incident", "user")


class CommsChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommsChannel
        fields = ("channel_id",)


class IncidentSerializer(serializers.ModelSerializer):
    reporter = ExternalUserSerializer(read_only=True)
    lead = ExternalUserSerializer()
    comms_channel = CommsChannelSerializer(read_only=True)

    class Meta:
        model = Incident
        fields = (
            "action_set",
            "comms_channel",
            "end_time",
            "impact",
            "lead",
            "pk",
            "report",
            "report_time",
            "reporter",
            "severity",
            "start_time",
            "summary",
        )

    def update(self, instance, validated_data):
        instance.end_time = validated_data.get("end_time", instance.end_time)
        instance.impact = validated_data.get("impact", instance.impact)

        new_lead = validated_data.get("lead", None)
        if new_lead:
            instance.lead = ExternalUser.objects.get(
                display_name=new_lead["display_name"],
                external_id=new_lead["external_id"],
            )

        instance.report = validated_data.get("report", instance.report)
        instance.start_time = validated_data.get("start_time", instance.start_time)
        instance.summary = validated_data.get("summary", instance.summary)
        instance.severity = validated_data.get("severity", instance.severity)

        instance.save()
        return instance
