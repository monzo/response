from datetime import datetime

from django.db import models

from response import core, slack
from response.core.models.user_external import ExternalUser
from response.core.util import sanitize


class IncidentManager(models.Manager):
    def create_incident(
        self,
        report,
        reporter,
        report_time,
        report_only,
        private=False,
        summary=None,
        impact=None,
        lead=None,
        severity=None,
    ):
        incident = self.create(
            report=report,
            reporter=reporter,
            report_time=report_time,
            report_only=report_only,
            private=private,
            start_time=report_time,
            summary=summary,
            impact=impact,
            lead=lead,
            severity=severity,
        )
        return incident


class Incident(models.Model):

    objects = IncidentManager()

    # Reporting info
    report = models.CharField(max_length=200)
    reporter = models.ForeignKey(
        ExternalUser,
        related_name="reporter",
        on_delete=models.PROTECT,
        blank=False,
        null=True,
    )
    report_time = models.DateTimeField()
    report_only = models.BooleanField(default=False)
    private = models.BooleanField(default=False)

    start_time = models.DateTimeField(null=False)
    end_time = models.DateTimeField(blank=True, null=True)

    # Additional info
    summary = models.TextField(
        blank=True, null=True, help_text="What's the high level summary?"
    )
    impact = models.TextField(
        blank=True, null=True, help_text="What impact is this having?"
    )
    lead = models.ForeignKey(
        ExternalUser,
        related_name="lead",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text="Who is leading?",
    )

    # Severity
    SEVERITIES = (("1", "critical"), ("2", "major"), ("3", "minor"), ("4", "trivial"))
    severity = models.CharField(
        max_length=10, blank=True, null=True, choices=SEVERITIES
    )

    def __str__(self):
        return self.report

    def comms_channel(self):
        try:
            return slack.models.CommsChannel.objects.get(incident=self)
        except slack.models.CommsChannel.DoesNotExist:
            return None

    def duration(self):
        delta = (self.end_time or datetime.now()) - self.start_time

        hours, remainder = divmod(delta.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)

        time_str = ""
        if hours > 0:
            hours = int(hours)
            time_str += f"{hours} hrs " if hours > 1 else f"{hours} hr "

        if minutes > 0:
            minutes = int(minutes)
            time_str += f"{minutes} mins " if minutes > 1 else f"{minutes} min "

        if hours == 0 and minutes == 0:
            seconds = int(seconds)
            time_str += f"{seconds} secs"

        return time_str.strip()

    def is_closed(self):
        return True if self.end_time else False

    def severity_text(self):
        for sev_id, text in self.SEVERITIES:
            if sev_id == self.severity:
                return text
        return None

    def severity_emoji(self):
        if not self.severity:
            return "☁️"

        return {"1": "⛈️", "2": "🌧️", "3": "🌦️", "4": "🌤️"}[self.severity]

    def status_text(self):
        if self.report_only:
            return "reported"
        elif self.is_closed():
            return "resolved"
        else:
            return "live"

    def status_emoji(self):
        if self.report_only:
            return ":notebook:"
        elif self.is_closed():
            return ":droplet:"
        else:
            return ":fire:"

    def badge_type(self):
        if self.is_closed():
            return "badge-success"
        elif self.severity and int(self.severity) < 3:
            return "badge-danger"
        return "badge-warning"

    def action_items(self):
        return core.models.Action.objects.filter(incident=self)

    def timeline_events(self):
        return core.models.TimelineEvent.objects.filter(incident=self)

    def save(self, *args, **kwargs):
        self.impact = sanitize(self.impact)
        self.report = sanitize(self.report)
        self.summary = sanitize(self.summary)
        super(Incident, self).save(*args, **kwargs)
