import logging
import requests

logger = logging.getLogger(__name__)


class GrafanaError(Exception):
    def __init__(self, message, grafana_error=None):
        self.message = message
        self.grafana_error = grafana_error


class GrafanaClient(object):
    def __init__(self, url, token):
        self.url = url
        self.token = token

    def create_annotation(self, **kwargs):
        logger.info("Create Annotation")

        payload = {
            "time": kwargs.get("time"),
            "tags": kwargs.get("tags"),
            "text": kwargs.get("text")
        }

        headers = {
            'Authorization': 'Bearer {}'.format(self.token),
            'Content-Type': 'application/json'
        }
        res = requests.post('{0}/api/{1}'.format(self.url, "annotations"),
                            headers=headers,
                            json=payload,
                            verify=True)

        result = res.json()
        res.close()
        if res.status_code == 200:
            return result
        raise GrafanaError(f"Failed to create annotations '{result}'")

    def update_annotation(self, annotation_id, time, time_end, text, tags):
        logger.info(f"Update Annotation: '{annotation_id}'")

        payload = {}
        if time:
            payload["time"] = int(time.timestamp() * 1000)
        if time_end:
            payload["timeEnd"] = int(time_end.timestamp() * 1000)
        if text:
            payload["text"] = text
        if tags:
            payload["tags"] = tags

        headers = {
            'Authorization': 'Bearer {}'.format(self.token),
            'Content-Type': 'application/json'
        }
        res = requests.patch('{0}/api/{1}/{2}'.format(self.url, "annotations", annotation_id),
                             headers=headers,
                             json=payload,
                             verify=True)

        result = res.json()
        res.close()
        if res.status_code == 200:
            return result
        raise GrafanaError(f"Failed to update annotation: '{annotation_id}': '{result}'")
