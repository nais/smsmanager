import logging
import os
import socket
import urllib.request

import requests
import uvicorn
from fastapi import FastAPI, Request, Response

from oncall import get_on_duty_number

logger = logging.getLogger("gunicorn.error")
app = FastAPI()
host = os.environ["HOST"]
username = os.environ["USERNAME"]
password = os.environ["PASSWORD"]
platformPartnerId = os.environ["PLATFORM_PARTNER_ID"]


def format_message(alert):
    status = alert["status"].upper()

    labels = alert["labels"]
    name = labels["alertname"]
    cluster_id = labels["tenant_cluster_id"]

    annotations = alert["annotations"]
    description = ""
    if "description" in annotations:
        description = annotations["description"]
    elif "summery" in annotations:
        description = annotations["summery"]
    elif "consequence" in annotations:
        description = annotations["consequence"]
    elif "action" in annotations:
        description = annotations["action"]
    else:
        description = "No description provided"

    logger.info("Alert=%, Status=%, Cluster=%", name, status, cluster_id)
    return "[{}] {} in {}\n{}".format(status, name, cluster_id, description)


def send_sms(message, recipients):
    recipients = recipients.split(",")

    status_code = 200
    for recipient in recipients:
        if not recipient.startswith("+"):
            recipient = "+47" + recipient

        url = "https://{}/sms/send".format(host)
        resp = requests.post(
            url,
            data={},
            auth=(username, password),
            json={
                "source": "NAIS",
                "platformId": "SMS",
                "platformPartnerId": platformPartnerId,
                "destination": recipient,
                "userData": message,
            },
        )

        if resp.status_code != 200:
            logger.error("Failed sending message: {}".format(resp.text))
            status_code = resp.status_code

    return status_code


@app.get("/")
async def index():
    return {"message": "Hello from {}".format(socket.gethostname())}


@app.post("/sms")
async def sms(recipients, request: Request, response: Response):
    json = await request.json()
    if len(json["alerts"]) > 1:
        logger.info(json["alerts"])

    common_labels = json.get("commonLabels", {})
    if common_labels.get("ping") == "nais-vakt":
        try:
            recipients = get_on_duty_number()
            logger.info("Resolved nais-vakt on-duty number: %s", recipients)
        except Exception as e:
            logger.error("Failed to resolve nais-vakt on-duty number: %s", e)
            response.status_code = 500
            return {"message": "Failed to resolve on-duty number"}

    response.status_code = 200
    for alert in json["alerts"]:
        try:
            message = format_message(alert)
            status_code = send_sms(message, recipients)

            if status_code > response.status_code:
                response.status_code = status_code
        except TypeError as e:
            logger.error(e)
            logger.error(alert)

    if response.status_code != 200:
        return {"message": "Failed to send SMS"}
    return {"message": "SMS sent"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("APP_PORT", 8080)))
