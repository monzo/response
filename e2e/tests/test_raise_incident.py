
def test_raise_incident_opens_dialog(slack_client, slack_httpserver):
    r = slack_client.post(
        "slack/slash_command",
        data={
            "user_id": "U123",
            "trigger_id": "foo",
        },
    )
    r.raise_for_status()
    slack_httpserver.check_assertions()
