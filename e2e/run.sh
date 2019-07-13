#!/bin/bash

set -euo pipefail

SKIP_CLEANUP=${SKIP_CLEANUP:-}

echo "🌐 Starting demo app..."
docker-compose -f "demo/docker-compose.yaml" up -d

function finish {
    echo ""
    echo "🔽 Cleaning up demo app .."
    docker-compose -f "demo/docker-compose.yaml" down 
    docker-compose -f "demo/docker-compose.yaml" rm 
}

if [[ -z "$SKIP_CLEANUP" ]]; then
    trap finish EXIT
fi


echo ""
echo "⏲️  Running e2e test container..."
docker run -it --rm \
    --name response-e2e \
    -e RESPONSE_ADDR=http://host.docker.internal:8000 \
    -p 9999:9999 \
    -v "$(pwd)":/usr/src/response \
    -w /usr/src/response/e2e \
    python:3.7 \
    bash _run_in_docker.sh

