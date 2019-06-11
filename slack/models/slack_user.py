from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class SlackUser(models.Model):
    user_id = models.CharField(max_length=50, primary_key=True, blank=False, null=False)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
