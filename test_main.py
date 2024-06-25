import socket
import os

from fastapi.testclient import TestClient

os.environ['endpoint'] = 'sms.no?recipients={}&message={}&username={}&password={}'
os.environ['username'] = 'testClient'
os.environ['password'] = '123'
os.environ['host'] = 'localhost'
os.environ['port'] = '8080'

from main import app, transform_text, format_message

client = TestClient(app)


def test_index():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from {}".format(socket.gethostname())}


class TestTransformText:
    def test_simple(self):
        textToTransform = "hello world"
        text = transform_text(textToTransform)
        assert text == "hello%20world"

    def test_newline(self):
        textToTransform = "hello\nworld"
        text = transform_text(textToTransform)
        assert text == "hello%0aworld"


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
        assert formatted == "[RESOLVED] Kafka connectivity test failing in nav-dev-gcp%0aKafka may be unavailable in cluster."

if __name__ == "__main__":
    test_index()
    TestTransformText().test_simple()
    TestTransformText().test_newline()
    TestFormatMessage().test_alert()
    print("All tests passed")
