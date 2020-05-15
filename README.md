SMSManager
==========

A simple webserver that sends alerts via a SMS endpoint.


## Testing

For now there is only manual testing.

Run the service locally with `uvicorn main:app --port 8080 --reload`, and test with the following:
```
curl -X POST -d @dummy-request.json localhost:8080/sms
```
