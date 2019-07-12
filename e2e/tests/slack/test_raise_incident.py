
from datetime import datetime


def test_raise_incident(slack_client, httpserver):
    print(httpserver.port)
    r = slack_client.post(
        "slack/slash_command",
        data={
            "user_id": "U123",
            "trigger_id": "13345224609.738474920.8088930838d88f008e0",
        },
    )
    r.raise_for_status()
