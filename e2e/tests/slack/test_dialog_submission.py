import json

def test_submit_dialog(slack_client, httpserver):
    httpserver.expect_oneshot_request(
        method="POST", uri="/api/dialog.open",
    ).respond_with_json({"ok": True})

    r = slack_client.post(
        "slack/action",
        data={
            "payload": json.dumps({
                "type": "dialog_submission",
                "callback_id": "incident-report-dialog",
                "user": {
                    "id": "U123",
                },
                "channel": {
                    "id": "C123",
                },
                "submission": {
                    "report": "",
                    "summary": "",
                    "impact": "",
                    "lead_id": "",
                    "severity": "",
                },
                "response_url": "",
                "state": "",
            }),
        },
    )
    r.raise_for_status()
    httpserver.check_assertions()
