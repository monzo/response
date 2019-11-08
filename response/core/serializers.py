import emoji_data_python
from rest_framework import serializers

from response.core.models import Action, Event, ExternalUser, Incident, TimelineEvent
from response.slack.models import CommsChannel
from response.slack.reference_utils import slack_to_human_readable


class ExternalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalUser
        fields = ("app_id", "external_id", "display_name", "full_name", "email")


class TimelineEventSerializer(serializers.ModelSerializer):
    metadata = serializers.JSONField(allow_null=True, required=False)
    # Read-only field for displaying human-readable slack references. Updates
    # should be applied to the text field.
    text_ui = serializers.SerializerMethodField()

    class Meta:
        model = TimelineEvent
        fields = ("id", "timestamp", "text", "event_type", "metadata", "text_ui")
        read_only_fields = ("id",)

    def get_text_ui(self, instance):
        text_ui = slack_to_human_readable(instance.text)
        text_ui = emoji_data_python.replace_colons(text_ui)
        return text_ui


class ActionSerializer(serializers.ModelSerializer):
    user = ExternalUserSerializer()
    # Read-only field for displaying human-readable slack references. Updates
    # should be applied to the details field.
    details_ui = serializers.SerializerMethodField()

    class Meta:
        model = Action
        fields = ("id", "details", "done", "user", "details_ui")
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

    def get_details_ui(self, instance):
        details_ui = slack_to_human_readable(instance.details)
        details_ui = emoji_data_python.replace_colons(details_ui)
        return details_ui


class CommsChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommsChannel
        fields = ("channel_id", "channel_name")


class IncidentSerializer(serializers.ModelSerializer):
    reporter = ExternalUserSerializer(read_only=True)
    lead = ExternalUserSerializer()
    comms_channel = CommsChannelSerializer(read_only=True)
    action_items = ActionSerializer(read_only=True, many=True)

    # This ensures we can't unset severity
    # https://www.django-rest-framework.org/api-guide/fields/#required
    # `required = False` means the field doesn't have to be included when the json request is
    # deserialised (including creation), and so it remains unchanged (if None, it remains None).
    # `allow_null` is set to False by default so we still demand a value is given _if_ it's sent in the json.
    severity = serializers.CharField(required=False)

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
            "report_only",
            "private",
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

        # we only allow setting private to true, we don't want to allow private incidents becoming public
        if not instance.private:
            instance.private = validated_data.get("private", instance.private)

        instance.save()
        return instance


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ("id", "timestamp", "event_type", "payload")
        read_only_fields = ("id", "timestamp", "event_type", "payload")
