#!/usr/bin/env python3
"""Downscale footer.png into footer-bg.png, the asset actually shipped.

footer.png is 1672x941 / 1.1MB — twenty times the weight of the rest of the
page for one decorative band. It is a dark image of smooth light streaks, so
it survives downscaling almost invisibly. This box-filters it to 1200px wide
and re-encodes with adaptive PNG filtering, which typically halves the payload.

Run after replacing footer.png. Pure stdlib: no Pillow on this machine.
"""
import zlib, struct, pathlib, sys

TARGET_W = 1200

src = pathlib.Path(__file__).resolve().parent.parent / 'footer.png'
dst = src.with_name('footer-bg.png')

d = src.read_bytes()
pos, idat, ihdr = 8, b'', None
while pos < len(d):
    ln = struct.unpack('>I', d[pos:pos+4])[0]
    typ = d[pos+4:pos+8]
    if typ == b'IHDR': ihdr = d[pos+8:pos+8+ln]
    elif typ == b'IDAT': idat += d[pos+8:pos+8+ln]
    pos += 12 + ln

W, H, depth, colour = (*struct.unpack('>II', ihdr[:8]), ihdr[8], ihdr[9])
BPP = {2: 3, 6: 4}.get(colour)
if depth != 8 or BPP is None:
    sys.exit(f'expected 8-bit RGB/RGBA, got depth={depth} colour_type={colour}')

stride = W * BPP
raw = zlib.decompress(idat)
prev, rows, i = bytearray(stride), [], 0
for _ in range(H):
    f = raw[i]; i += 1
    line = bytearray(raw[i:i+stride]); i += stride
    if f:
        for x in range(stride):
            a = line[x-BPP] if x >= BPP else 0
            b = prev[x]
            c = prev[x-BPP] if x >= BPP else 0
            if   f == 1: line[x] = (line[x] + a) & 255
            elif f == 2: line[x] = (line[x] + b) & 255
            elif f == 3: line[x] = (line[x] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p-a), abs(p-b), abs(p-c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[x] = (line[x] + pr) & 255
    rows.append(bytes(line)); prev = line

# ---- box downscale -------------------------------------------------------
scale = TARGET_W / W
OW = TARGET_W
OH = max(1, round(H * scale))
out_rows = []
for oy in range(OH):
    y0, y1 = int(oy * H / OH), max(int(oy * H / OH) + 1, int((oy + 1) * H / OH))
    line = bytearray()
    for ox in range(OW):
        x0, x1 = int(ox * W / OW), max(int(ox * W / OW) + 1, int((ox + 1) * W / OW))
        n = (y1 - y0) * (x1 - x0)
        acc = [0, 0, 0]
        for y in range(y0, y1):
            r = rows[y]
            for x in range(x0, x1):
                o = x * BPP
                acc[0] += r[o]; acc[1] += r[o+1]; acc[2] += r[o+2]
        line += bytes((acc[0]//n, acc[1]//n, acc[2]//n))
    out_rows.append(bytes(line))

# ---- adaptive filtering, then deflate -----------------------------------
def filtered(cur, prev_row):
    """Pick the filter with the smallest absolute-sum, the standard heuristic."""
    n = len(cur)
    best, best_sum = None, None
    for ft in range(5):
        out = bytearray()
        for x in range(n):
            a = cur[x-3] if x >= 3 else 0
            b = prev_row[x]
            c = prev_row[x-3] if x >= 3 else 0
            if   ft == 0: v = cur[x]
            elif ft == 1: v = cur[x] - a
            elif ft == 2: v = cur[x] - b
            elif ft == 3: v = cur[x] - (a + b) // 2
            else:
                p = a + b - c
                pa, pb, pc = abs(p-a), abs(p-b), abs(p-c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                v = cur[x] - pr
            out.append(v & 255)
        s = sum(v if v < 128 else 256 - v for v in out)
        if best_sum is None or s < best_sum:
            best, best_sum = (ft, out), s
    return best

buf = bytearray()
zero = bytes(OW * 3)
prev_row = zero
for r in out_rows:
    ft, data = filtered(r, prev_row)
    buf.append(ft); buf += data
    prev_row = r

def chunk(tag, data):
    return (struct.pack('>I', len(data)) + tag + data
            + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff))

dst.write_bytes(b'\x89PNG\r\n\x1a\n'
                + chunk(b'IHDR', struct.pack('>IIBBBBB', OW, OH, 8, 2, 0, 0, 0))
                + chunk(b'IDAT', zlib.compress(bytes(buf), 9))
                + chunk(b'IEND', b''))

print(f'{dst.name}: {OW}x{OH}, {len(dst.read_bytes())//1024}KB '
      f'(source {W}x{H}, {len(d)//1024}KB)')
