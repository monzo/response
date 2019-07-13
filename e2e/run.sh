#!/bin/bash

set -euo pipefail

SKIP_CLEANUP=${SKIP_CLEANUP:-}

echo "🌤️  Configuring environment"

if [[ -e "demo/.env" ]]; then
    echo "❌  Error: demo/.env already exists. Please remove, as this script will overwrite anything in that file"
    exit 1
fi

cat <<EOF >demo/.env
SLACK_TOKEN=xoxp-e2e-tests
SLACK_SIGNING_SECRET=${SLACK_SIGNING_SECRET:-e2e-secret}
INCIDENT_CHANNEL_NAME=incidents
INCIDENT_BOT_NAME=e2eincident
PAGERDUTY_ENABLED=False
ENCRYPTED_FIELD_KEY=J/4QbmqservbeAPifIR8gI1EmBKdeB4yTGPeWzCPtng=

DJANGO_SETTINGS_MODULE=demo.settings.dev
SLACK_API_MOCK=host.docker.internal:9999
EOF

echo "🌐 Starting demo app..."
docker-compose -f "demo/docker-compose.yaml" up -d

function finish() {
    echo ""
    echo "🔽 Cleaning up demo app..."
    docker-compose -f "demo/docker-compose.yaml" down
    docker-compose -f "demo/docker-compose.yaml" rm

    echo "🔽 Cleaning up env file..."
    rm -rf demo/.env
}

if [[ -z "$SKIP_CLEANUP" ]]; then
    trap finish EXIT
fi

echo ""
echo "⏲️  Running e2e test container..."
docker run -it --rm \
    --name response-e2e \
    -e RESPONSE_ADDR=http://host.docker.internal:8000 \
    --env-file demo/.env \
    -p 9999:9999 \
    -v "$(pwd)":/usr/src/response \
    -w /usr/src/response/e2e \
    python:3.7 \
    bash _run_in_docker.sh
