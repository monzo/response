from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, Http404

from response.core.models import Incident
from response.slack.models import PinnedMessage, UserStats


def incident_doc(request: HttpRequest, incident_id: str):

    try:
        incident = Incident.objects.get(pk=incident_id)
    except Incident.DoesNotExist:
        raise Http404("Incident does not exist")

    events = PinnedMessage.objects.filter(incident=incident).order_by('timestamp')
    user_stats = UserStats.objects.filter(incident=incident).order_by('-message_count')[:5]

    return render(request, template_name='incident_doc.html', context={
        "incident": incident,
        "events": events,
        "user_stats": user_stats,
    })
