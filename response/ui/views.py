from django.http import Http404, HttpRequest
from django.shortcuts import render

from response.core.models import Action, Incident
from response.decorators import response_login_required
from response.slack.models import PinnedMessage, UserStats


@response_login_required
def home(request: HttpRequest):
    incidents = Incident.objects.all
    return render(request, template_name="home.html", context={"incidents": incidents})


@response_login_required
def incident_doc(request: HttpRequest, incident_id: str):
    try:
        incident = Incident.objects.get(pk=incident_id)
    except Incident.DoesNotExist:
        raise Http404("Incident does not exist")

    events = PinnedMessage.objects.filter(incident=incident).order_by("timestamp")
    actions = Action.objects.filter(incident=incident).order_by("created_date")
    user_stats = UserStats.objects.filter(incident=incident).order_by("-message_count")[
        :5
    ]
    return render(
        request,
        template_name="incident_doc.html",
        context={
            "incident": incident,
            "events": events,
            "actions": actions,
            "user_stats": user_stats,
        },
    )
