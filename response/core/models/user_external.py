from django.contrib.auth.models import User
from django.db import models


class ExternalUserManager(models.Manager):
    def get_or_create_slack(self, *args, **kwargs):
        return self.get_or_create(app_id="slack", *args, **kwargs)

    def update_or_create_slack(self, *args, **kwargs):
        return self.update_or_create(app_id="slack", *args, **kwargs)


class ExternalUser(models.Model):
    class Meta:
        unique_together = ("owner", "app_id", "external_id")

    owner = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    app_id = models.CharField(max_length=50, blank=False, null=False)
    external_id = models.CharField(max_length=50, blank=False, null=False)
    display_name = models.CharField(max_length=50, blank=False, null=False)
    full_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)

    objects = ExternalUserManager()

    def __str__(self):
        return f"{self.display_name or self.external_id} ({self.app_id})"
