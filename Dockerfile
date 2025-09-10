FROM cgr.dev/chainguard/python:latest-dev AS builder
WORKDIR /app
RUN python -m venv venv
ENV PATH="/app/venv/bin:$PATH"
COPY ./requirements.txt /code/requirements.txt
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir --upgrade -r /code/requirements.txt

FROM europe-north1-docker.pkg.dev/cgr-nav/pull-through/nav.no/python:latest
WORKDIR /app
COPY main.py .
COPY --from=builder /app/venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
