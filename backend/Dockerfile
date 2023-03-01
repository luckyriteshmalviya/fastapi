FROM python:3.8

WORKDIR /fastapi-app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

ENV NEW_RELIC_CONFIG_FILE=newrelic.ini 

ENV NEW_RELIC_DISTRIBUTED_TRACING_ENABLED=true 

ENV NEW_RELIC_APPLICATION_LOGGING_ENABLED=true

ENV NEW_RELIC_APPLICATION_LOGGING_FORWARDING_ENABLED=true

ENV NEW_RELIC_APP_NAME="MopidBackendStage"

ENV NEW_RELIC_LICENSE_KEY=506b2ab619455835a4fa6c4b24118b9e0770NRAL

ENTRYPOINT ["newrelic-admin", "run-program"]

CMD ["uvicorn", "main:app", "--proxy-headers", "--workers", "4","--host", "0.0.0.0", "--port", "8000"]