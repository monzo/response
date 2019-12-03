from django.db import models

from response.core.models.incident import Incident
from response.core.models.user_external import ExternalUser
from response.core.util import sanitize


class Action(models.Model):
    created_date = models.DateTimeField(null=True, auto_now_add=True)
    details = models.TextField(blank=True, default="")
    done = models.BooleanField(default=False)
    done_date = models.DateTimeField(null=True)
    due_date = models.DateTimeField(null=True)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    user = models.ForeignKey(
        ExternalUser, on_delete=models.CASCADE, blank=False, null=False
    )

    # Priority
    PRIORITIES = (("1", "high"), ("2", "medium"), ("3", "low"))
    priority = models.CharField(
        max_length=10, blank=True, null=True, choices=PRIORITIES
    )

    # Type
    TYPES = (("1", "detective"), ("2", "preventative"), ("3", "corrective"))
    type = models.CharField(max_length=10, blank=True, null=True, choices=TYPES)

    def icon(self):
        return "🔜️"

    def __str__(self):
        return f"{self.details}"

    def save(self, *args, **kwargs):
        self.details = sanitize(self.details)
        super(Action, self).save(*args, **kwargs)
