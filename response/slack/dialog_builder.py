from django.conf import settings
from slackclient import SlackClient

from response.slack.slack_utils import SlackError


slack_token = settings.SLACK_TOKEN
slack_client = SlackClient(slack_token)


class Dialog:
    def __init__(self, title, submit_label, elements=None, state=None):
        self.title = title
        self.submit_label = submit_label
        self.state = state
        self.elements = elements

    def add_element(self, element):
        if not self.elements:
            self.elements = []
        self.elements.append(element)

    def set_state(self, state):
        self.state = state

    def build_dialog(self, callback_id):
        elements = []
        for element in self.elements:
            elements.append(element.serialize())

        dialog = {
            "title": self.title,
            "submit_label": self.submit_label,
            "callback_id": callback_id,
            "state": self.state,
            "elements": elements,
        }
        return dialog

    def send_open_dialog(self, callback_id, trigger_id):
        """
        Open the dialog
        """
        response = slack_client.api_call(
            "dialog.open",
            trigger_id=trigger_id,
            dialog=self.build_dialog(callback_id),
        )

        if not response.get("ok", False):
            raise SlackError(
                'Failed to open dialog : {}'.format(response['error']))


class Element:
    def __init__(self, label, name, optional, hint, subtype, value, placeholder):
        self.label = label
        self.name = name
        self.optional = optional
        self.hint = hint
        self.subtype = subtype
        self.value = value
        self.placeholder = placeholder

    def serialize(self):
        return {k: v for k, v in vars(self).items() if v}


class Text(Element):
    def __init__(self, label=None, name=None, optional=False, hint=None, subtype=None, value=None, placeholder=None):
        super().__init__(label, name, optional, hint, subtype, value, placeholder)
        self.type = "text"


class TextArea(Element):
    def __init__(self, label=None, name=None, optional=False, hint=None, subtype=None, value=None, placeholder=None):
        super().__init__(label, name, optional, hint, subtype, value, placeholder)
        self.type = "textarea"


class SelectWithOptions(Element):
    def __init__(self, options, label=None, name=None, optional=False, hint=None, subtype=None, value=None, placeholder=None):
        super().__init__(label, name, optional, hint, subtype, value, placeholder)
        self.type = "select"
        self.options = [{"label": l, "value": v} for l, v in options]


class SelectFromUsers(Element):
    def __init__(self, label=None, name=None, optional=False, hint=None, subtype=None, value=None, placeholder=None):
        super().__init__(label, name, optional, hint, subtype, value, placeholder)
        self.type = "select"
        self.data_source = "users"
