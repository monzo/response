"""
This is a slightly more complex migration. This change adds a new CommsChannel
field to cache the channel name, updating it when the Slack API notifies us of
a channel rename. For existing CommsChannel in the DB, we need to populate
the channel_name by connecting to the Slack API.

This applies the migration in three stages. First, we add the new field, but
make it nullable, so there's no need to set a default. The next step iterates
over existing CommsChannels, and refreshes the name from the Slack API.

Finally, now that every CommsChannel has a channel_name set, we alter the field
so that a value is required.
"""

from django.conf import settings
from django.db import OperationalError, migrations, models

from response.slack.client import SlackError


def set_comms_channel_names(apps, schema_editor):
    CommsChannel = apps.get_model("response", "CommsChannel")
    for comms_channel in CommsChannel.objects.all().iterator():
        try:
            channel_name = settings.SLACK_CLIENT.get_channel_name(
                comms_channel.channel_id
            )
            if not channel_name:
                channel_name = "<channel not found>"
        except SlackError as e:
            raise OperationalError(
                f"""Error connecting to the Slack API: {str(e)}
⚠️  This migration requires access to the Slack API to set CommsChannel.channel_name on existing CommsChannel object. Please make sure that the SLACK_TOKEN environment variable is set to a valid value."""
            )

        comms_channel.channel_name = channel_name
        comms_channel.save()


class Migration(migrations.Migration):

    dependencies = [("response", "0008_externaluser_email")]

    operations = [
        migrations.AddField(
            model_name="commschannel",
            name="channel_name",
            field=models.CharField(null=True, max_length=80),
            preserve_default=False,
        ),
        migrations.RunPython(set_comms_channel_names, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="commschannel",
            name="channel_name",
            field=models.CharField(null=False, max_length=80),
            preserve_default=False,
        ),
    ]
