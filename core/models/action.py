from datetime import datetime
from django.db import models
from core.models.incident import Incident


class Action(models.Model):
    details = models.TextField(blank=True, default="")
    done = models.BooleanField(default=False)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=50, blank=False, null=False)

    def icon(self):
        return "🔜️"

    def __str__(self):
        return f"{self.details}"