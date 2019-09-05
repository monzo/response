from django.core.urls import include, path

urlpatterns = (
    path("", include("response.core.urls")),
    path("", include("response.slack.urls")),
    path("", include("response.ui.urls")),
)
