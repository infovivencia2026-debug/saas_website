#!/usr/bin/env bash
# Preview the site locally. No dependencies: the site is three files and
# python3 already ships a static server.
#
#   ./serve.sh [port]        default 8080  ->  http://localhost:8080/
set -euo pipefail
cd "$(dirname "$0")"
exec python3 -m http.server "${1:-8080}" --bind 127.0.0.1
