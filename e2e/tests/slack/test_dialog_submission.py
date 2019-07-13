from datetime import datetime
import json

def test_submit_dialog_creates_incident(client, slack_client, slack_httpserver):
    slack_httpserver.expect_request(
        method="POST", uri="/api/users.info",
    ).respond_with_json({
        "ok": True,
        "user": {
            "name": "Opsy McOpsface",
            "profile": {
                "real_name":  "Opsy McOpsface",
            },
        },
    })

    slack_httpserver.expect_request(
        method="POST", uri="/api/chat.postMessage",
    ).respond_with_json({"ok": True})

    incident_ts = datetime.now().timestamp()

    report = f"something's wrong ({incident_ts})"

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
                    "report": report,
                    "summary": "not sure what tho",
                    "impact": "lots",
                    "lead": "U123",
                    "severity": "major",
                },
                "response_url": "",
                "state": "",
            }),
        },
    )
    r.raise_for_status()
    slack_httpserver.check_assertions()

    r = client.get("/core/incidents")
    r.raise_for_status()
    incidents = r.json()

    assert incidents[-1]["report"] == report