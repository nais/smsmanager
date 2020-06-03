import logging
import os
import socket
import urllib.request

from fastapi import FastAPI, Request

logger = logging.getLogger('gunicorn.error')
app = FastAPI()
UnformattedURL = os.environ['sms_endpoint']
username = os.environ['username']
password = os.environ['password']
cluster = os.getenv('cluster', 'uspesifisert')

def transformText(text):
    return text.replace(' ', '%20')

def formatMessage(alert):
    return '[{}] {} in {}%0a{}'.format(
        alert['status'].upper(),
        alert['labels']['alertname'],
        cluster,
        alert['annotations']['description'])

def sendSMS(message, recipients):
    url = UnformattedURL.format(recipients, message, username, password)
    response = urllib.request.urlopen(url).read()
    if response != b'Request processed OK':
        logger.error(response)

@app.get("/")
async def index():
    return {"message": "Hello from {}".format(socket.gethostname())}

@app.post("/sms")
async def sms(request: Request):
    json = await request.json()
    for alert in json['alerts']:
        message = formatMessage(alert)
        sendSMS(transformText(message), alert['annotations']['recipients'])
