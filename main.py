import logging
import os
import socket
import urllib.request

import uvicorn
from fastapi import FastAPI, Request

logger = logging.getLogger('gunicorn.error')
app = FastAPI()
endpoint = os.environ['endpoint']
username = os.environ['username']
password = os.environ['password']
host = os.environ['host']
port = os.environ['port']


def transform_text(text):
    return text.replace(' ', '%20').replace('\n', '%0a')


def format_message(alert):
    status = alert['status'].upper()

    labels = alert['labels']
    name = labels['alertname']
    cluster_id = labels['tenant_cluster_id']

    annotations = alert['annotations']
    description = ''
    if 'description' in annotations:
        description = annotations['description']
    elif 'summery' in annotations:
        description = annotations['summery']
    elif 'consequence' in annotations:
        description = annotations['consequence']
    elif 'action' in annotations:
        description = annotations['action']
    else:
        description = 'No description provided'

    return '[{}] {} in {}%0a{}'.format(
        status,
        name,
        cluster_id,
        description)


def send_sms(message, recipients):
    formatted = endpoint.format(host, port, recipients, message, username, password)
    response = urllib.request.urlopen(formatted).read()
    if response != b'Request processed OK':
        logger.error(response)


@app.get("/")
async def index():
    return {"message": "Hello from {}".format(socket.gethostname())}


@app.post("/sms")
async def sms(request: Request, recipients):
    json = await request.json()
    if len(json['alerts']) > 1:
        logger.info(json['alerts'])

    for alert in json['alerts']:
        try:
            message = format_message(alert)
            send_sms(transform_text(message), recipients)
        except TypeError as te:
            logger.error(te)
            logger.error(alert)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('APP_PORT', 8080)))
