
def test_raise_incident_opens_dialog(slack_client, httpserver):
    httpserver.expect_oneshot_request(
        method="POST", uri="/api/dialog.open",
    ).respond_with_json({"ok": True})

    r = slack_client.post(
        "slack/slash_command",
        data={
            "user_id": "U123",
            "trigger_id": "foo",
        },
    )
    r.raise_for_status()
    httpserver.check_assertions()
