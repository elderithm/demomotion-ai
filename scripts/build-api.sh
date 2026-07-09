#!/usr/bin/env bash
set -euo pipefail
PROJECT_ID=${PROJECT_ID:?PROJECT_ID is required}
REGION=${REGION:-asia-northeast1}
REPO=${REPO:-demomotion-ai}
IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/api:latest"
gcloud builds submit . --tag "$IMAGE" --project "$PROJECT_ID"
echo "$IMAGE"
