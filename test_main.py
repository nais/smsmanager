import socket
import os

from fastapi.testclient import TestClient

os.environ["USERNAME"] = "testClient"
os.environ["PASSWORD"] = "123"
os.environ["HOST"] = "localhost"
os.environ["PLATFORM_PARTNER_ID"] = "test"
os.environ["CALENDAR_ICS_URL"] = "https://example.com/calendar.ics"
os.environ["TENANT"] = "localhost"

from main import app, format_message

client = TestClient(app)


def test_index():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from {}".format(socket.gethostname())}


class TestFormatMessage:
    def test_alert(self):
        alert = {
            "status": "firing",
            "labels": {
                "alertname": "kyrrev5",
                "container": "unleash",
                "endpoint": "http",
                "instance": "10.43.41.46:4242",
                "job": "yrkesskade",
                "k8s_cluster_name": "management",
                "namespace": "nais-system",
                "ping": "nais-vakt",
                "pod": "yrkesskade-59cbdb586c-hxqtx",
                "service": "yrkesskade",
                "severity": "critical",
            },
            "annotations": {
                "action": "Check Kyrre / application / load balancer / network",
                "consequence": "Kyrre down / not accessible",
                "summary": "Probe kyrre is failing",
            },
            "startsAt": "2026-06-25T13:56:16.642Z",
            "endsAt": "0001-01-01T00:00:00Z",
            "generatorURL": "/graph?g0.expr=up%7Bk8s_cluster_name%3D%22management%22%7D+%3E%3D+1&g0.tab=1",
            "fingerprint": "61266cd23c82d9dd",
        }
        formatted = format_message(alert)
        assert (
            formatted
            == "[FIRING] kyrrev5 in localhost/management\nKyrre down / not accessible"
        )
