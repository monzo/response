from datetime import datetime
from unittest.mock import MagicMock

from slackclient import SlackClient


class MockSlack(object):
    def __init__(self):
        self.slack_api_calls = {}
        self.mock = MagicMock(spec=SlackClient)
        self.mock.api_call.side_effect = self.handle_slack_api_call

    def handle_slack_api_call(self, name, *args, **kwargs):
        self.slack_api_calls[name] = {"args": args, "kwargs": kwargs}
        if name == "users.info":
            return {
                "ok": True,
                "user": {
                    "name": "Opsy McOpsface",
                    "profile": {"real_name": "Opsy McOpsface"},
                },
            }
        elif name == "dialog.open":
            return {"ok": True, "ts": str(datetime.now().timestamp())}
        elif name == "chat.postMessage":
            return {"ok": True, "ts": str(datetime.now().timestamp())}
        elif name == "chat.update":
            return {"ok": True, "ts": str(datetime.now().timestamp())}
        elif name == "chat.postEphemeral":
            return {"ok": True, "message_ts": str(datetime.now().timestamp())}

        raise RuntimeError("unhandled slack call:" + name)
