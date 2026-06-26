import logging
import os
from datetime import date

import requests
from icalendar import Calendar
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

CALENDAR_ICS_URL = os.environ["CALENDAR_ICS_URL"]

_retry = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist={429, 500, 502, 503, 504},
    raise_on_status=True,
)
_session = requests.Session()
_session.mount("https://", HTTPAdapter(max_retries=_retry))
_session.mount("http://", HTTPAdapter(max_retries=_retry))


def get_on_duty_number() -> str:
    """
    Look up the current on-duty person from the nais-vakt Google Calendar ICS feed
    and return their phone number from the event description.

    Retries up to 3 times with exponential backoff on connection errors and
    transient HTTP failures (429, 500, 502, 503, 504).
    Raises an exception if the lookup fails for any reason.
    """
    resp = _session.get(CALENDAR_ICS_URL, timeout=10)
    resp.raise_for_status()

    cal = Calendar.from_ical(resp.text)
    today = date.today()

    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        dtstart = component.get("DTSTART")
        dtend = component.get("DTEND")
        description = component.get("DESCRIPTION")

        if not dtstart or not dtend or not description:
            continue

        start = dtstart.dt
        end = dtend.dt

        if hasattr(start, "date"):
            start = start.date()
        if hasattr(end, "date"):
            end = end.date()

        if start <= today < end:
            phone = str(description).strip()
            logger.info("On-duty phone found for week starting %s", start)
            return phone

    raise RuntimeError("No on-duty event found in calendar for today")
