from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, Http404
from django.db.models import Q
from datetime import datetime, timedelta

from core.models import Incident
from slack.models import PinnedMessage, UserStats


def incident_doc(request: HttpRequest, incident_id: str):

    try:
        incident = Incident.objects.get(pk=incident_id)
    except Incident.DoesNotExist:
        raise Http404("Incident does not exist")

    events = PinnedMessage.objects.filter(incident=incident)
    user_stats = UserStats.objects.filter(incident=incident).order_by('-message_count')[:5]

    return render(request, template_name='incident_doc.html', context={
        "incident": incident,
        "events": events,
        "user_stats": user_stats,
    })

def active_incidents(request: HttpRequest):

    active_incidents = Incident.objects.filter(end_time__isnull=True)

    return render(request, template_name="incidents.html", context={
        "incidents": active_incidents,
        "incident_filter": "Active",
        "show_status": False
    })

def recent_incidents(request: HttpRequest):

    filter_date = datetime.now()-timedelta(days=14)
    recent_incidents = Incident.objects.filter(Q(end_time__isnull=True)|Q(report_time__gte=filter_date))

    return render(request, template_name="incidents.html", context={
        "incidents": recent_incidents,
        "incident_filter": "Recent",
        "show_status": True
    })