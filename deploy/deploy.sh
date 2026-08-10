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

# HERO.png and deploy/make-mask.py are kept for when a hero image is wanted
# again — nothing on the page references the mask at the moment, so it is not
# shipped. Re-add hero-wave.png to the tar line below to bring it back.

echo "==> Packing"
TARBALL="$(mktemp -t vivencia-XXXXXX.tar.gz)"
tar -czf "$TARBALL" index.html styles.css

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
for path in "" styles.css; do
  code="$(curl -s -o /dev/null -w '%{http_code}' "https://vivencia.187-127-178-100.sslip.io/$path")"
  printf '    %s  /%s\n' "$code" "$path"
  [ "$code" = "200" ] || { echo "!!! /$path returned $code"; exit 1; }
done

echo "==> Live: https://vivencia.187-127-178-100.sslip.io/  (release $RELEASE)"
echo "    Roll back:  ssh $TARGET 'rm -rf $ROOT && mv $ROOT.prev $ROOT && systemctl reload nginx'"
