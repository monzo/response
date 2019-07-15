from datetime import datetime
from django.db import models

from response.core.models import Incident, ExternalUser
from response.slack.slack_utils import get_user_profile, GetOrCreateSlackExternalUser

class UserStats(models.Model):
    user = models.ForeignKey(ExternalUser, on_delete=models.CASCADE, blank=False, null=False)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, blank=False, null=False)

    join_time = models.DateTimeField(null=True)
    message_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ("incident", "user")

    @staticmethod
    def increment_message_count(incident, user_id):
        name = get_user_profile(user_id)['name']
        user = GetOrCreateSlackExternalUser(external_id=user_id, display_name=name)

        user_stats, created = UserStats.objects.get_or_create(incident=incident, user=user)

        if created:
            user_stats.join_time = datetime.now()

        user_stats.message_count += 1
        user_stats.save()

    def __str__(self):
        return f"{self.user.display_name} - {self.incident}"
