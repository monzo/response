from datetime import datetime
from django.db import models

from core.models import Incident


class UserStats(models.Model):
    user_id = models.CharField(max_length=50, blank=False, null=False)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, blank=False, null=False)

    join_time = models.DateTimeField(null=True)
    message_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ("incident", "user_id")

    @staticmethod
    def increment_message_count(incident, user_id):
        user_stats, created = UserStats.objects.get_or_create(incident=incident, user_id=user_id)

        if created:
            user_stats.join_time = datetime.now()

        user_stats.message_count += 1
        user_stats.save()

    def __str__(self):
        return f"{self.user_id} - {self.incident}"
