from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("response", "0007_delete_incidentextension")]

    operations = [
        migrations.AddField(
            model_name="externaluser",
            name="email",
            field=models.CharField(blank=True, max_length=100, null=True),
        )
    ]
