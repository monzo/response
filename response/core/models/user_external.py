from datetime import datetime
from django.db import models
from django.contrib.auth.models import User


class ExternalUser(models.Model):
    class Meta:
        unique_together = ("owner", "app_id")

    owner = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    app_id = models.CharField(max_length=50, blank=False, null=False)
    external_id = models.CharField(max_length=50, blank=False, null=False)
    display_name = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return f'{self.display_name or self.external_id} ({self.app_id})'