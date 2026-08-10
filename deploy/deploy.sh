#!/usr/bin/env bash
# Ship the static site to the server and swap it in atomically.
#
#   ./deploy/deploy.sh [user@host] [remote-root]
#
# Defaults to root@187.127.178.100:/var/www/vivencia-site. Nothing is built
# on the server — it only ever receives finished files. The previous release
# is kept as <root>.prev so a rollback is one move.
set -euo pipefail

TARGET="${1:-root@187.127.178.100}"
ROOT="${2:-/var/www/vivencia-site}"
RELEASE="$(date +%Y%m%d-%H%M%S)"

cd "$(dirname "$0")/.."

# Shipping the source PNGs as-is, by request. They are heavy — hero.png is
# 1.7MB and footer.png 1.1MB — and ./deploy/optimize-images.sh can re-encode
# them to WebP at ~24KB each on the server, which has ffmpeg. Both are shipped:
# styles.css uses image-set() so a browser takes the 24KB WebP when it can and
# the PNG when it cannot — which means BOTH must exist on the server.
for img in hero-art.png hero-art.webp footer.png footer.webp; do
  [ -f "$img" ] || { echo "!!! $img missing"; exit 1; }
done

echo "==> Packing"
TARBALL="$(mktemp -t vivencia-XXXXXX.tar.gz)"
tar -czf "$TARBALL" index.html styles.css hero-art.png hero-art.webp footer.png footer.webp

echo "==> Uploading to $TARGET"
scp -q "$TARBALL" "$TARGET:/tmp/vivencia-$RELEASE.tar.gz"
rm -f "$TARBALL"

echo "==> Installing release $RELEASE"
# Unpack beside the live directory and swap with a rename, so a visitor never
# sees a half-written tree.
ssh "$TARGET" bash -s <<REMOTE
set -euo pipefail
rm -rf "$ROOT.new"
mkdir -p "$ROOT.new"
tar -xzf "/tmp/vivencia-$RELEASE.tar.gz" -C "$ROOT.new"
rm -rf "$ROOT.prev"
[ -d "$ROOT" ] && mv "$ROOT" "$ROOT.prev" || true
mv "$ROOT.new" "$ROOT"
chown -R www-data:www-data "$ROOT" 2>/dev/null || true
rm -f "/tmp/vivencia-$RELEASE.tar.gz"
nginx -t >/dev/null && systemctl reload nginx
REMOTE

echo "==> Verifying"
# Verify from the server, not from here. This workstation's outbound 443 is
# not always reachable, and a network fault on the operator's machine must not
# be reported as a broken deploy.
ssh "$TARGET" bash -s <<'REMOTE'
set -euo pipefail
fail=0
for path in "" styles.css hero-art.png hero-art.webp footer.png footer.webp; do
  code="$(curl -sS --max-time 20 -o /dev/null -w '%{http_code}' \
          "https://vivencia.187-127-178-100.sslip.io/$path")"
  printf '    %s  /%s\n' "$code" "$path"
  [ "$code" = "200" ] || fail=1
done
exit $fail
REMOTE

echo "==> Live: https://vivencia.187-127-178-100.sslip.io/  (release $RELEASE)"
echo "    Roll back:  ssh $TARGET 'rm -rf $ROOT && mv $ROOT.prev $ROOT && systemctl reload nginx'"
