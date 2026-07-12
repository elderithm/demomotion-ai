#!/usr/bin/env bash
# Build the web dashboard and push it to Artifact Registry for Cloud Run.
# Run from the repo root. NEXT_PUBLIC_API_BASE_URL is inlined at build time, so
# pass the deployed API's Cloud Run URL. Cloud Run runs linux/amd64.
set -euo pipefail
PROJECT_ID=${PROJECT_ID:?PROJECT_ID is required}
API_BASE_URL=${API_BASE_URL:?API_BASE_URL is required (the deployed API Cloud Run URL)}
REGION=${REGION:-asia-northeast1}
NAME=${NAME:-demomotion-ai}
IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$NAME/web:latest"

gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet
docker build --platform linux/amd64 -f apps/web/Dockerfile \
  --build-arg "NEXT_PUBLIC_API_BASE_URL=$API_BASE_URL" -t "$IMAGE" .
docker push "$IMAGE"
echo "$IMAGE"
