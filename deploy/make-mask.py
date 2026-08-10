#!/usr/bin/env python3
"""Derive hero-wave.png (the CSS alpha mask) from HERO.png (the artwork).

HERO.png is ink on an opaque white ground — every pixel is alpha 255. A CSS
mask reads alpha, so the source cannot be used as a mask directly, and pasting
it onto the tinted hero would punch a white rectangle through the atmosphere.

This rewrites its luminance as alpha: ink opaque, paper transparent. Output is
greyscale+alpha (PNG colour type 4), which is half the payload of RGBA and
carries everything a mask needs. Run after replacing HERO.png.
"""
import zlib, struct, pathlib, sys

src = pathlib.Path(__file__).resolve().parent.parent / 'HERO.png'
dst = src.with_name('hero-wave.png')

d = src.read_bytes()
if d[:8] != b'\x89PNG\r\n\x1a\n':
    sys.exit('HERO.png is not a PNG')

pos, idat, ihdr = 8, b'', None
while pos < len(d):
    ln = struct.unpack('>I', d[pos:pos+4])[0]
    typ = d[pos+4:pos+8]
    if typ == b'IHDR': ihdr = d[pos+8:pos+8+ln]
    elif typ == b'IDAT': idat += d[pos+8:pos+8+ln]
    pos += 12 + ln

W, H, depth, colour = (*struct.unpack('>II', ihdr[:8]), ihdr[8], ihdr[9])
if (depth, colour) != (8, 6):
    sys.exit(f'expected 8-bit RGBA, got depth={depth} colour_type={colour}')

BPP, stride = 4, W * 4
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

# Crop to the ink. HERO.png carries a wide margin of blank paper (the top
# ~31% is empty), and a CSS `cover` mask on a wide, short box will happily
# land inside that emptiness and render nothing at all. Cropping here means
# the mask is all artwork, so no combination of mask-size and mask-position
# can show a blank band.
def row_ink(y):
    r = rows[y]
    return sum(255 - ((r[x*4]*299 + r[x*4+1]*587 + r[x*4+2]*114) // 1000)
               for x in range(0, W, 4)) / (len(range(0, W, 4)) * 255)

inked = [y for y in range(H) if row_ink(y) > 0.01]
if not inked:
    sys.exit('HERO.png appears to be blank')
pad = 8
top, bot = max(0, inked[0] - pad), min(H - 1, inked[-1] + pad)
CH = bot - top + 1
print(f'  ink rows {inked[0]}..{inked[-1]} of {H} -> cropping to {W}x{CH}')

out = bytearray()
for y in range(top, bot + 1):
    out.append(0)                                   # filter: none
    r = rows[y]
    for x in range(W):
        o = x * 4
        lum = (r[o]*299 + r[o+1]*587 + r[o+2]*114) // 1000
        out += bytes((0, 255 - lum))                # grey, alpha = ink coverage

def chunk(tag, data):
    return (struct.pack('>I', len(data)) + tag + data
            + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff))

dst.write_bytes(b'\x89PNG\r\n\x1a\n'
                + chunk(b'IHDR', struct.pack('>IIBBBBB', W, CH, 8, 4, 0, 0, 0))
                + chunk(b'IDAT', zlib.compress(bytes(out), 9))
                + chunk(b'IEND', b''))
print(f'{dst.name}: {W}x{CH}, {len(dst.read_bytes())//1024}KB '
      f'(source {len(d)//1024}KB)')
