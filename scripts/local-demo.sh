#!/usr/bin/env bash
set -euo pipefail
make dev-api &
make dev-demo &
make dev-web &
wait
