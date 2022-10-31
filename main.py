import logging
import os
import socket
import urllib.request

import uvicorn
from fastapi import FastAPI, Request

logger = logging.getLogger('gunicorn.error')
app = FastAPI()
endpoint = os.environ['sms_endpoint']
username = os.environ['username']
password = os.environ['password']
cluster = os.getenv('cluster', 'uspesifisert')


def transform_text(text):
    return text.replace(' ', '%20').replace('\n', '%0a')


def format_message(alert):
    return '[{}] {} in {}%0a{}'.format(
        alert['status'].upper(),
        alert['labels']['alertname'],
        cluster,
        alert['annotations']['description'])


def send_sms(message, recipients):
    formatted = endpoint.format(recipients, message, username, password)
    response = urllib.request.urlopen(formatted).read()
    if response != b'Request processed OK':
        logger.error(response)


@app.get("/")
async def index():
    return {"message": "Hello from {}".format(socket.gethostname())}


@app.post("/sms")
async def sms(request: Request):
    json = await request.json()
    if len(json['alerts']) > 1:
        logger.info(json['alerts'])

    for alert in json['alerts']:
        message = format_message(alert)
        send_sms(transform_text(message), alert['annotations']['recipients'])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('APP_PORT')))
