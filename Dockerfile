# Stage 1 - Install Python Requirement and Response
FROM python:3.7-slim as builder

WORKDIR /src

RUN apt-get update && apt-get install -y gcc libpq-dev

RUN pip install uwsgi

COPY ./response/ /src/response/
COPY ./setup.py /src/
COPY ./README.md /src/
COPY ./MANIFEST.in /src/
COPY ./LICENSE /src/

RUN pip install .

# Stage 2 - Install/Obtain supercronic for cron
FROM python:3.7-slim as supercronic

RUN apt-get update && apt-get install -y curl

ENV SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/download/v0.1.11/supercronic-linux-amd64 \
  SUPERCRONIC=supercronic-linux-amd64 \
  SUPERCRONIC_SHA1SUM=a2e2d47078a8dafc5949491e5ea7267cc721d67c

RUN curl -fsSLO "$SUPERCRONIC_URL" \
  && echo "${SUPERCRONIC_SHA1SUM}  ${SUPERCRONIC}" | sha1sum -c - \
  && chmod +x "$SUPERCRONIC" \
  && mv "$SUPERCRONIC" "/usr/local/bin/${SUPERCRONIC}" \
  && ln -s "/usr/local/bin/${SUPERCRONIC}" /usr/local/bin/supercronic

# Stage 3 - FINAL - Put the pieces together
FROM python:3.7-slim

WORKDIR /app
ENTRYPOINT ["/app/entrypoint.sh"]

RUN apt-get update && apt-get install -y wget netcat postgresql-client && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=supercronic /usr/local/bin/supercronic /usr/local/bin/supercronic
COPY --from=builder /usr/local/lib/python3.7/site-packages/ /usr/local/lib/python3.7/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

COPY ./app/ /app/
COPY ./entrypoint.sh /app/entrypoint.sh
COPY ./crontab /app/crontab

RUN mkdir -p /app/static && chown -R nobody /app/static

USER nobody