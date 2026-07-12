#!/usr/bin/env bash
# Build the API container and push it to Artifact Registry for Cloud Run.
# Run from the repo root. Cloud Run runs linux/amd64, so build for that platform
# (on Apple Silicon this uses emulation).
set -euo pipefail
PROJECT_ID=${PROJECT_ID:?PROJECT_ID is required}
REGION=${REGION:-asia-northeast1}
NAME=${NAME:-demomotion-ai}
IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$NAME/api:latest"

gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet
docker build --platform linux/amd64 -f services/api/Dockerfile -t "$IMAGE" .
docker push "$IMAGE"
echo "$IMAGE"
