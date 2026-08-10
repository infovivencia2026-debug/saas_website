#!/usr/bin/env bash
# Derive the shipped hero artwork from hero.png.
#
# The current source is a perspective ray fan: measured convergence at 99%
# across / 16% down (right edge, upper area), the top ~20% empty, and energy
# filling everything below. It is used full-bleed behind the hero rather than
# as a bottom band, so no crop is applied — only a WebP encode for weight.
#
# ffmpeg lives on the deploy server, not this workstation.
set -euo pipefail
HOST="${1:-root@187.127.178.100}"
cd "$(dirname "$0")/.."

cp hero.png hero-art.png                       # PNG ships at full resolution

echo "==> encoding hero-art.webp"
scp -q hero.png "$HOST:/tmp/_hero_in.png"
ssh "$HOST" "ffmpeg -y -loglevel error -i /tmp/_hero_in.png -vf scale=1600:-1:flags=lanczos \
             -c:v libwebp -quality 82 -compression_level 6 /tmp/_hero_art.webp && rm -f /tmp/_hero_in.png"
scp -q "$HOST:/tmp/_hero_art.webp" hero-art.webp
ssh "$HOST" 'rm -f /tmp/_hero_art.webp'

printf '    hero-art.png  %s\n    hero-art.webp %s\n' \
  "$(du -h hero-art.png | cut -f1)" "$(du -h hero-art.webp | cut -f1)"
