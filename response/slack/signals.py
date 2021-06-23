from urllib.parse import urljoin

from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse

from response.core.models import Incident, add_incident_update_event
from response.core.serializers import ExternalUserSerializer
from response.slack.models import HeadlinePost


@receiver(post_save, sender=Incident)
def update_headline_after_incident_save(sender, instance, **kwargs):
    """
    Reflect changes to incidents in the headline post

    Important: this is called in the synchronous /incident flow so must remain fast (<2 secs)

    """
    try:
        headline_post = HeadlinePost.objects.get(incident=instance)
        headline_post.update_in_slack()

    except HeadlinePost.DoesNotExist:
        headline_post = HeadlinePost.objects.create_headline_post(incident=instance)


@receiver(pre_save, sender=Incident)
def prompt_incident_report(sender, instance: Incident, **kwargs):
    """
    Prompt incident lead to complete a report when an incident is closed.
    """

    try:
        prev_state = Incident.objects.get(pk=instance.pk)
    except Incident.DoesNotExist:
        # Incident hasn't been saved yet, nothing to do here.
        return

    if instance.is_closed() and not prev_state.is_closed():
        user_to_notify = instance.lead or instance.reporter
        doc_url = urljoin(
            settings.SITE_URL,
            reverse("incident_doc", kwargs={"incident_id": instance.pk}),
        )
        settings.SLACK_CLIENT.send_message(
            user_to_notify.external_id,
            f"👋 Don't forget to fill out an incident report here: {doc_url}",
        )


@receiver(post_save, sender=HeadlinePost)
def update_headline_after_save(sender, instance, **kwargs):
    """
    Reflect changes to headline posts in slack

    """
    instance.update_in_slack()


@receiver(pre_save, sender=Incident)
def add_timeline_events(sender, instance: Incident, **kwargs):
    try:
        prev_state = Incident.objects.get(pk=instance.pk)
    except Incident.DoesNotExist:
        # Incident hasn't been saved yet, nothing to do here.
        return

    for attr_name in instance.attributes:
        if attr_name=="severity":
            UpdateSeverityEvent(attr_name).update_incident_event(prev_state,instance)
        elif attr_name=="lead":
            UpdateLeadEvent(attr_name).update_incident_event(prev_state,instance)
        else:
            UpdateIncidentEvent(attr_name).update_incident_event(prev_state,instance)


#Generic handler for updating stat 
class UpdateIncidentEvent():
    def __init__(self,prev_state, instance, attr_name=""):
        self.prev_state=prev_state
        self.instance=instance
        self.attr_name=attr_name

    def getText(self):
        text=f'Incident environment '
        prev_attr=getattr(self.prev_state, self.attr_name)
        inst_attr=getattr(self.instance, self.attr_name)
        if prev_attr:
            return text + f'updated from "{prev_attr}" to "{inst_attr}"'
        else:
            return text + f'added: "{inst_attr}"'

    def isUpdated(self):
        return getattr(self.prev_state, self.attr_name) != getattr(self.instance, self.attr_name)

    def add_incident_event(
            self,
            incident=None,
            update_type=None,
            text=None,
            old_value=None,
            new_value=None
        ):
        #lets us override update_incident_event and pass in custom parameters
        if not incident:
            incident=self.instance
        if not update_type:
            update_type=self.attr_name
        if not text:
            text=self.getText()
        if not old_value:
            old_value=getattr(self.prev_state, self.attr_name)
        if not new_value:
            new_value=getattr(self.instance, self.attr_name)

        add_incident_update_event(
            incident=incident,
            update_type=update_type,
            text=text,
            old_value=old_value,
            new_value=new_value,
        )

    def update_incident_event(self):
        #to be overriden to add custom values
        self.add_incident_event()     


class UpdateLeadEvent(UpdateIncidentEvent):

    def __init__(self, prev_state, instance, attr_name=""):
        super.__init__(attr_name, prev_state, instance)

    def update_incident_event(self):  
        self.add_incident_event(
            old_value=ExternalUserSerializer(self.prev_state.lead).data if self.prev_state.lead  else None,
            new_value=ExternalUserSerializer(self.instance.lead).data if self.instance.lead  else None
    )  

    def getText(self):
        if not self.prev_state.lead:
            return f"{self.instance.lead.display_name} was added as incident lead" 
        elif self.instance.lead:
            return f"Incident lead changed from {self.prev_state.lead.display_name} to {self.instance.lead.display_name}"
        else:
            return f"{self.prev_state.lead.display_name} was removed as incident lead"


class UpdateSeverityEvent(UpdateIncidentEvent):

    def __init__(self, prev_state, instance, attr_name=""):
        super.__init__(prev_state, instance, attr_name)

    def update_incident_event(self):  
        self.add_incident_event(
            update_type="incident_severity",
            old_value={
                "id": self.prev_state.severity,
                "text": self.prev_state.severity_text() if self.prev_state else "",
            },
            new_value={   
                "id": self.instance.severity, 
                "text": self.instance.severity_text()
            }
    )     
