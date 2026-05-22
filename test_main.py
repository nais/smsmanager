import socket
import os

from fastapi.testclient import TestClient

os.environ["USERNAME"] = "testClient"
os.environ["PASSWORD"] = "123"
os.environ["HOST"] = "localhost"
os.environ["PLATFORM_PARTNER_ID"] = "test"
os.environ["SPREADSHEET_ID"] = "test"

from main import app, format_message

client = TestClient(app)


def test_index():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from {}".format(socket.gethostname())}


class TestFormatMessage:
    def test_alert(self):
        alert = {
            "status": "resolved",
            "labels": {
                "alertname": "Kafka connectivity test failing",
                "instance": "http://contests/kafka",
                "job": "probe/nais-system/contests-probes",
                "namespace": "nais-system",
                "ping": "nais-vakt",
                "prometheus": "nais-system/monitoring-nais-prometheus",
                "severity": "critical",
                "tenant": "nav",
                "tenant_cluster": "dev-gcp",
                "tenant_cluster_id": "nav-dev-gcp",
            },
            "annotations": {
                "action": "Check logs for contests appliction",
                "consequence": "Kafka may be unavailable in cluster.",
            },
            "startsAt": "2024-06-25T13:43:23.303Z",
            "endsAt": "2024-06-25T13:56:23.303Z",
            "generatorURL": "https://nais-prometheus.dev-gcp.nav.cloud.nais.io/graph?g0.expr=probe_success%7Binstance%3D~%22http%3A%2F%2Fcontests%2Fkafka%22%7D+%3D%3D+0&g0.tab=1",
            "fingerprint": "8184e4ed0380b9f7",
        }
        formatted = format_message(alert)
        assert (
            formatted
            == "[RESOLVED] Kafka connectivity test failing in nav-dev-gcp\nKafka may be unavailable in cluster."
        )
