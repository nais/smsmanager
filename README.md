SMSManager
==========

A simple webserver that sends alerts via a SMS endpoint.


## Testing

For now there is only manual testing.

Run the service locally with `uvicorn main:app --port 8080 --reload`, and test with the following:
```
curl -X POST -d @dummy-request.json localhost:8080/sms
```

## nais-vakt SMS alerts

In management environments the chart creates an `AlertmanagerConfig` that routes alerts labelled `ping=nais-vakt` to `smsmanager`.
This is controlled by `naisvakt.smsAlertsEnabled` (default `true`).

To disable it for an environment (e.g. `dev-nais`), set `naisvakt.smsAlertsEnabled` to `false` for the `smsmanager` feature in that environment in Fasit.
Only the `AlertmanagerConfig` is removed; the smsmanager Deployment, Service and API keep running.
