from django.db import models
from core.models import Incident, ExternalUser
from datetime import datetime

class Source(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class TimelineManager(models.Manager):
    def new_event(self, source, *args, **kwargs):
        if not 'timestamp' in kwargs:
            kwargs['timestamp'] = datetime.now()

        source, created = Source.objects.get_or_create(name=source)
        return self.create(source=source, *args, **kwargs)


class Timeline(models.Model):
    objects = TimelineManager()

    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, blank=True, null=True)
    author = models.ForeignKey(ExternalUser, on_delete=models.PROTECT, blank=True, null=True)

    timestamp = models.DateTimeField()
    editable = models.BooleanField(default=True)
    source = models.ForeignKey(Source, on_delete=models.PROTECT)
    text = models.TextField(max_length=200)

    def __str__(self):
        return f'{self.source} - {self.author}: {self.text}'
