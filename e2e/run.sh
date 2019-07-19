#!/bin/bash

set -euo pipefail

SKIP_CLEANUP=${SKIP_CLEANUP:-}

function dc() {
    docker-compose -f "demo/docker-compose.yaml" -f "e2e/docker-compose.override.yaml" ${@}
}

echo "ℹ️  Docker version is $(docker --version)"
echo "ℹ️  docker-compose version is $(docker-compose --version)"

echo ""
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

DJANGO_SETTINGS_MODULE=demo.settings.dev
SLACK_API_MOCK=e2e-test:9999
EOF

echo "🌐 Starting demo app..."
dc up -d

function finish() {
    echo ""
    echo "🔽 Cleaning up demo app..."
    dc down
    dc rm

    echo "🔽 Cleaning up env file..."
    rm -rf demo/.env
}

if [[ -z "$SKIP_CLEANUP" ]]; then
    trap finish EXIT
fi

echo ""
echo "⏲️  Attaching to e2e test container..."

dc logs -f e2e-test
