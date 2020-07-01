import socket

from fastapi.testclient import TestClient

from os import environ

environ['sms_endpoint'] = 'sms.no?recipients={}&message={}&username={}&password={}'
environ['username'] = 'testClient'
environ['password'] = '123'

from main import app, transformText, formatMessage

client = TestClient(app)

def test_index():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'message': 'Hello from {}'.format(socket.gethostname())}

class TestTransformText:
    def test_simple(self):
        textToTransform = 'hello world'
        text = transformText(textToTransform)
        assert text == 'hello%20world'

    def test_newline(self):
        textToTransform = 'hello\nworld'
        text = transformText(textToTransform)
        assert text == 'hello%0aworld'
