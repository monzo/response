from django.db import models

from response.core.models import Incident


class Notification(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    key = models.CharField(max_length=30)
    time = models.DateTimeField()
    repeat_count = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("incident", "key")

    def __str__(self):
        nice_date = self.time.strftime("%Y-%m-%d %H:%M:%S")
        return f"{nice_date} - {self.incident} - {self.key}"
