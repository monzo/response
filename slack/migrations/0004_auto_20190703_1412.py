# Generated by Django 2.2.2 on 2019-07-03 14:12

from django.db import migrations, models
import django.db.models.deletion


def move_pinnedmessage_to_timeline(apps, schema_editor):
    Timeline = apps.get_model('core', 'Timeline')
    Source = apps.get_model('core', 'Source')
    PinnedMessage = apps.get_model('slack', 'PinnedMessage')

    for pm in PinnedMessage.objects.all():
        source, created = Source.objects.get_or_create(name='slack_pin')
        timeline = Timeline(incident=pm.incident,
                        author=pm.author,
                        source=source,
                        text=pm.text,
                        timestamp=pm.timestamp)
        timeline.save()
        pm.timeline = timeline
        pm.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_source_timeline'),
        ('slack', '0003_auto_20190624_1422'),
    ]

    operations = [
        migrations.AddField(
            model_name='pinnedmessage',
            name='timeline',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Timeline'),
            preserve_default=False,
        ),
        migrations.RunPython(move_pinnedmessage_to_timeline),
        migrations.AlterField(
            model_name='pinnedmessage',
            name='timeline',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Timeline'),
        ),
        migrations.RemoveField(
            model_name='pinnedmessage',
            name='author',
        ),
        migrations.RemoveField(
            model_name='pinnedmessage',
            name='incident',
        ),
        migrations.RemoveField(
            model_name='pinnedmessage',
            name='text',
        ),
        migrations.RemoveField(
            model_name='pinnedmessage',
            name='timestamp',
        ),
    ]
