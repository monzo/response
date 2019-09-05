from django.conf import settings

INCIDENT_REPORT_DIALOG = "incident-report-dialog"
INCIDENT_EDIT_DIALOG = "incident-edit-dialog"

SLACK_API_MOCK = getattr(settings, "SLACK_API_MOCK", None)

if SLACK_API_MOCK:
    from urllib.parse import urlparse
    from slackclient.slackrequest import requests

    old_post = requests.post

    import logging

    def fake_post(url, *args, **kwargs):
        parsed = urlparse(url)
        newurl = parsed._replace(netloc=SLACK_API_MOCK, scheme="http")
        logging.info(f"Fake Slack client request: HTTP POST {SLACK_API_MOCK} {newurl}")
        return old_post(newurl.geturl(), *args, **kwargs)

    requests.post = fake_post
