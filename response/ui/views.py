from django.http import Http404, HttpRequest, HttpResponseForbidden
from django.shortcuts import render

from response.core.models import Incident
from response.decorators import response_login_required
from response.slack.models import PinnedMessage, UserStats


@response_login_required
def incident_doc(request: HttpRequest, incident_id: str):
    try:
        incident = Incident.objects.get(pk=incident_id)
    except Incident.DoesNotExist:
        raise Http404("Incident does not exist")

    # private incident details cannot be viewed by anyone
    if incident.private:
        return HttpResponseForbidden()

    events = PinnedMessage.objects.filter(incident=incident).order_by("timestamp")
    user_stats = UserStats.objects.filter(incident=incident).order_by("-message_count")[
        :5
    ]

    return render(
        request,
        template_name="incident_doc.html",
        context={"incident": incident, "events": events, "user_stats": user_stats},
    )
