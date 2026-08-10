#!/usr/bin/env bash
# Turn the source PNGs into the web assets the page actually loads.
#
#   ./deploy/optimize-images.sh
#
# hero.png and footer.png are large smooth-gradient renders — PNG is the wrong
# container for them (hero.png alone is 1.6MB). This resizes and re-encodes
# them to WebP, which typically cuts them by 15-30x with no visible loss.
#
# There is no ffmpeg, Pillow or ImageMagick on this workstation, but the
# deploy server has ffmpeg — so the encode is done there and the result
# pulled back. The outputs are committed, so this only needs re-running when
# a source image changes.
set -euo pipefail

HOST="${1:-root@187.127.178.100}"
cd "$(dirname "$0")/.."

encode() {           # <source> <output> <width> <quality>
  local src="$1" out="$2" w="$3" q="$4"
  [ -f "$src" ] || { echo "    skip $src (missing)"; return; }
  echo "==> $src -> $out (${w}px, q$q)"
  scp -q "$src" "$HOST:/tmp/_opt_in.png"
  ssh "$HOST" "ffmpeg -y -loglevel error -i /tmp/_opt_in.png \
      -vf scale=${w}:-1:flags=lanczos -c:v libwebp -quality ${q} -compression_level 6 \
      /tmp/_opt_out.webp && rm -f /tmp/_opt_in.png"
  scp -q "$HOST:/tmp/_opt_out.webp" "$out"
  ssh "$HOST" 'rm -f /tmp/_opt_out.webp'
  printf '    %s -> %s\n' \
    "$(du -h "$src"  | cut -f1)" \
    "$(du -h "$out" | cut -f1)"
}

encode hero.png   hero.webp   1600 82
encode footer.png footer.webp 1400 80

echo "==> done"
