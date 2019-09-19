from rest_framework import serializers

from response.core.models import Action, ExternalUser, Incident, TimelineEvent
from response.slack.models import CommsChannel


class ExternalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalUser
        fields = ("app_id", "external_id", "display_name", "full_name", "email")


class TimelineEventSerializer(serializers.ModelSerializer):
    metadata = serializers.JSONField(allow_null=True)

    class Meta:
        model = TimelineEvent
        fields = ("id", "timestamp", "text", "event_type", "metadata")
        read_only_fields = ("id",)


class ActionSerializer(serializers.ModelSerializer):
    user = ExternalUserSerializer()

    class Meta:
        model = Action
        fields = ("id", "details", "done", "user")
        read_only_fields = ("id",)

    def create(self, validated_data):
        user = ExternalUser.objects.get(
            app_id=validated_data["user"]["app_id"],
            display_name=validated_data["user"]["display_name"],
            external_id=validated_data["user"]["external_id"],
            full_name=validated_data["user"]["full_name"],
        )
        validated_data["user"] = user
        return Action.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if "user" in validated_data:
            instance.user = ExternalUser.objects.get(
                app_id=validated_data["user"]["app_id"],
                display_name=validated_data["user"]["display_name"],
                external_id=validated_data["user"]["external_id"],
                full_name=validated_data["user"]["full_name"],
            )
        instance.details = validated_data.get("details", instance.details)
        instance.done = validated_data.get("done", instance.done)
        instance.save()
        return instance


class CommsChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommsChannel
        fields = ("channel_id", "channel_name")


class IncidentSerializer(serializers.ModelSerializer):
    reporter = ExternalUserSerializer(read_only=True)
    lead = ExternalUserSerializer()
    comms_channel = CommsChannelSerializer(read_only=True)
    action_items = ActionSerializer(read_only=True, many=True)

    class Meta:
        model = Incident
        fields = (
            "action_items",
            "comms_channel",
            "end_time",
            "impact",
            "is_closed",
            "lead",
            "id",
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
                full_name=new_lead["full_name"],
            )

        instance.report = validated_data.get("report", instance.report)
        instance.start_time = validated_data.get("start_time", instance.start_time)
        instance.summary = validated_data.get("summary", instance.summary)
        instance.severity = validated_data.get("severity", instance.severity)

        instance.save()
        return instance
