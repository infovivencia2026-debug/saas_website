#!/usr/bin/env bash
# Derive the hero artwork actually used on the page from hero.png.
#
# Measured on the source: the horizon arc's mass sits at 55-65% of the image
# height, the light point at ~3%, and the bottom ~20% is empty paper. That
# empty band is dead weight at the bottom of the hero and pushes the arc up
# into the headline, so it is cropped off here. Cropping once means the CSS
# only has to anchor the element, not fight the file's padding.
#
# ffmpeg lives on the deploy server, not this workstation.
set -euo pipefail
HOST="${1:-root@187.127.178.100}"
cd "$(dirname "$0")/.."

CROP="1668:770:0:30"     # w:h:x:y — keeps the light point, drops the dead base

echo "==> cropping hero.png ($CROP)"
scp -q hero.png "$HOST:/tmp/_hero_in.png"
ssh "$HOST" "ffmpeg -y -loglevel error -i /tmp/_hero_in.png -vf crop=${CROP} /tmp/_hero_art.png && \
             ffmpeg -y -loglevel error -i /tmp/_hero_art.png -vf scale=1600:-1:flags=lanczos \
               -c:v libwebp -quality 82 -compression_level 6 /tmp/_hero_art.webp"
scp -q "$HOST:/tmp/_hero_art.png"  hero-art.png
scp -q "$HOST:/tmp/_hero_art.webp" hero-art.webp
ssh "$HOST" 'rm -f /tmp/_hero_in.png /tmp/_hero_art.png /tmp/_hero_art.webp'

python3 - <<'PY'
import struct
for f in ('hero-art.png',):
    d = open(f,'rb').read()
    w,h = struct.unpack('>II', d[16:24])
    print(f'    {f}: {w}x{h}  aspect {w/h:.3f}  {len(d)//1024}KB')
PY
printf '    hero-art.webp: %s\n' "$(du -h hero-art.webp | cut -f1)"
