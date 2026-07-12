#!/usr/bin/env bash
# Generate a narrated demo video (mp4) from a web app URL and a goal, using the
# containerized DemoMotion pipeline. See ../SKILL.md.
set -euo pipefail

IMAGE="ghcr.io/elderithm/demomotion-ai-api:latest"
URL=""; GOAL=""
LANG_CODE="en-US"; ASPECT="16:9"; OUTPUT="demo.mp4"
AI="demo"; TTS="demo"; STORAGE="local"
GCP_PROJECT=""; GCP_LOCATION="us-central1"
PORT="8080"

usage() {
  cat >&2 <<EOF
Usage: generate.sh --url URL --goal "GOAL" [options]

Required:
  --url URL            Web app URL to record (public, preview, or localhost)
  --goal "TEXT"        What the demo should show

Options:
  --language CODE      Narration language, e.g. en-US, ja-JP  (default: en-US)
  --aspect RATIO       16:9 or 9:16                           (default: 16:9)
  --output PATH        Where to write the MP4 (relative = current dir; default: demo.mp4)
  --image REF          API container image                    (default: public GHCR image)
  --ai PROVIDER        demo | vertex                          (default: demo)
  --tts PROVIDER       demo | google                          (default: demo)
  --storage PROVIDER   local | gcs                            (default: local)
  --gcp-project ID     Google Cloud project (for vertex/google/gcs)
  --gcp-location LOC   Vertex location                        (default: us-central1)
  --port PORT          Host port for the API                  (default: 8080)
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --url) URL="$2"; shift 2;;
    --goal) GOAL="$2"; shift 2;;
    --language) LANG_CODE="$2"; shift 2;;
    --aspect) ASPECT="$2"; shift 2;;
    --output) OUTPUT="$2"; shift 2;;
    --image) IMAGE="$2"; shift 2;;
    --ai) AI="$2"; shift 2;;
    --tts) TTS="$2"; shift 2;;
    --storage) STORAGE="$2"; shift 2;;
    --gcp-project) GCP_PROJECT="$2"; shift 2;;
    --gcp-location) GCP_LOCATION="$2"; shift 2;;
    --port) PORT="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1;;
  esac
done

[ -n "$URL" ] && [ -n "$GOAL" ] || { echo "Error: --url and --goal are required." >&2; usage; exit 1; }
command -v docker  >/dev/null 2>&1 || { echo "Error: docker is required and must be running." >&2; exit 1; }
command -v curl    >/dev/null 2>&1 || { echo "Error: curl is required." >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Error: python3 is required." >&2; exit 1; }

# Let the browser inside the container reach a dev server on the host.
TARGET_URL="$URL"
case "$URL" in
  *localhost*|*127.0.0.1*)
    TARGET_URL=$(printf '%s' "$URL" | sed -e 's#localhost#host.docker.internal#g' -e 's#127\.0\.0\.1#host.docker.internal#g');;
esac

CID="demomotion-skill-$$"
cleanup() { docker rm -f "$CID" >/dev/null 2>&1 || true; }
trap cleanup EXIT

run_args=(run -d --name "$CID" -p "$PORT:8080"
  --add-host=host.docker.internal:host-gateway
  -e "AI_PROVIDER=$AI" -e "TTS_PROVIDER=$TTS" -e "STORAGE_PROVIDER=$STORAGE")

if [ "$AI" = vertex ] || [ "$TTS" = google ] || [ "$STORAGE" = gcs ]; then
  ADC="$HOME/.config/gcloud/application_default_credentials.json"
  [ -f "$ADC" ] || { echo "Error: vertex/google/gcs need local credentials. Run: gcloud auth application-default login" >&2; exit 1; }
  [ -n "$GCP_PROJECT" ] || { echo "Error: --gcp-project is required for vertex/google/gcs." >&2; exit 1; }
  run_args+=(-v "$HOME/.config/gcloud:/root/.config/gcloud:ro"
    -e "GOOGLE_APPLICATION_CREDENTIALS=/root/.config/gcloud/application_default_credentials.json"
    -e "GCP_PROJECT_ID=$GCP_PROJECT" -e "GCP_LOCATION=$GCP_LOCATION")
fi

echo "Starting the DemoMotion API (pulling $IMAGE if needed)..."
docker "${run_args[@]}" "$IMAGE" >/dev/null

echo "Waiting for the API to become ready..."
ready=""
for _ in $(seq 1 60); do
  if curl -sf "http://localhost:$PORT/healthz" >/dev/null 2>&1; then ready=1; break; fi
  sleep 3
done
[ -n "$ready" ] || { echo "Error: API did not become ready." >&2; docker logs "$CID" 2>&1 | tail -30 >&2; exit 1; }

payload=$(DM_URL="$TARGET_URL" DM_GOAL="$GOAL" DM_LANG="$LANG_CODE" DM_ASPECT="$ASPECT" python3 -c \
  'import json,os; print(json.dumps({"url":os.environ["DM_URL"],"goal":os.environ["DM_GOAL"],"language":os.environ["DM_LANG"],"aspect_ratio":os.environ["DM_ASPECT"]}))')

job=$(curl -sf -X POST "http://localhost:$PORT/v1/video-jobs" -H 'Content-Type: application/json' -d "$payload" \
  | python3 -c 'import sys,json; print(json.loads(sys.stdin.read(), strict=False)["id"])')
echo "Submitted job $job — generating (this takes ~1-2 minutes)..."

status=""
for _ in $(seq 1 300); do
  body=$(curl -sf "http://localhost:$PORT/v1/video-jobs/$job") || { sleep 3; continue; }
  status=$(printf '%s' "$body" | python3 -c 'import sys,json; print(json.loads(sys.stdin.read(), strict=False)["status"])')
  echo "  status=$status"
  [ "$status" = completed ] && break
  if [ "$status" = failed ]; then
    printf '%s' "$body" | python3 -c 'import sys,json; print(json.loads(sys.stdin.read(), strict=False).get("error",""))' >&2
    docker logs "$CID" 2>&1 | tail -30 >&2
    exit 1
  fi
  sleep 3
done
[ "$status" = completed ] || { echo "Error: job did not complete in time." >&2; exit 1; }

curl -sf "http://localhost:$PORT/v1/video-jobs/$job/download" -o "$OUTPUT"
echo "Done. Wrote:"
ls -lh "$OUTPUT"
