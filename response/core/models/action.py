from datetime import datetime
from django.db import models
from response.core.models.incident import Incident
from response.core.models.user_external import ExternalUser


class Action(models.Model):
    details = models.TextField(blank=True, default="")
    done = models.BooleanField(default=False)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    user = models.ForeignKey(ExternalUser, on_delete=models.CASCADE, blank=False, null=False)

    def icon(self):
        return "🔜️"

    def __str__(self):
        return f"{self.details}"
