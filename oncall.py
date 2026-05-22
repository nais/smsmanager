import csv
import io
import logging
import os
from datetime import date

import requests

logger = logging.getLogger("gunicorn.error")

SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]
SCHEDULE_GID = "0"
CONTACTS_GID = "1532689156"


def _csv_export_url(gid: str) -> str:
    return (
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
        f"/export?format=csv&gid={gid}"
    )


def _fetch_csv(gid: str) -> list[dict]:
    url = _csv_export_url(gid)
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    reader = csv.DictReader(io.StringIO(resp.text))
    return list(reader)


def get_on_duty_number() -> str:
    """
    Look up the current on-duty person from the Nais vakt Google Spreadsheet
    and return their phone number.

    Raises an exception if the lookup fails for any reason.
    """
    schedule_rows = _fetch_csv(SCHEDULE_GID)

    today = date.today()
    best_start = None
    best_person = None

    for row in schedule_rows:
        raw_date = (row.get("StartDato") or "").strip()
        person = (row.get("Person") or "").strip()
        if not raw_date or not person:
            continue
        try:
            start_date = date.fromisoformat(raw_date)
        except ValueError:
            continue
        if start_date <= today:
            if best_start is None or start_date > best_start:
                best_start = start_date
                best_person = person

    if best_person is None:
        raise RuntimeError("Could not determine on-duty person from schedule sheet")

    logger.info("On-duty person: %s (week starting %s)", best_person, best_start)

    contact_rows = _fetch_csv(CONTACTS_GID)

    for row in contact_rows:
        name = (row.get("Navn") or "").strip()
        phone = (row.get("Telefon") or "").strip()
        if name.lower() == best_person.lower() and phone:
            return phone

    raise RuntimeError(f"On-duty person '{best_person}' not found in contacts sheet")
