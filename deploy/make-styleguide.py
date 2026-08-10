#!/usr/bin/env python3
"""Generate styleguide.html from the real stylesheet.

The swatches, hexes and contrast ratios are read out of styles.css rather than
typed in, so the guide cannot drift from the site. Re-run after a theme change.
"""
import re, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
css = (root / 'styles.css').read_text()
tokens = dict(re.findall(r'(--[a-z0-9-]+):\s*([^;]+);', css.split(':root {')[1].split('\n}')[0]))
tokens = {k: v.strip() for k, v in tokens.items()}

def lum(h):
    h = h.lstrip('#')
    if len(h) == 3: h = ''.join(c * 2 for c in h)
    c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    c = [v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4 for v in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]

def ratio(f, b):
    a, c = lum(f), lum(b)
    return (max(a, c) + .05) / (min(a, c) + .05)

GROUPS = [
    ('Cobalt ramp',  ['--brand-900','--brand-800','--brand-700','--brand-600','--brand-500','--brand-400','--brand-300']),
    ('Grounds',      ['--ground-2','--ground','--ground-3','--canvas','--surface-2','--surface']),
    ('Light type',   ['--heading','--heading-2','--body','--muted']),
    ('Dark type',    ['--on-ground-hi','--on-ground','--on-ground-2','--on-ground-3']),
    ('Surfaces',     ['--brand-soft','--brand-tint','--surface-3','--border']),
]

def swatch(name):
    v = tokens.get(name, '')
    hexv = v if v.startswith('#') else ''
    dark = lum(hexv) < .32 if hexv else False
    ink = '#ffffff' if dark else '#0a1d42'
    on_w  = f'{ratio(hexv, "#ffffff"):.1f}' if hexv else '—'
    on_d  = f'{ratio(hexv, "#07152f"):.1f}' if hexv else '—'
    return f'''<div class="sw" style="background:{v};color:{ink}">
      <span class="sw__n">{name.replace('--','')}</span>
      <span class="sw__h">{v.upper()}</span>
      <span class="sw__c">on white {on_w}:1 · on midnight {on_d}:1</span>
    </div>'''

groups = '\n'.join(
    f'<h3>{title}</h3>\n<div class="sws">' + '\n'.join(swatch(n) for n in names) + '</div>'
    for title, names in GROUPS)

doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Vivencia — style guide</title>
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Michroma&family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="styles.css">
<style>
  body {{ background: var(--canvas); }}
  .guide {{ max-width: 76rem; margin-inline: auto; padding: 4rem var(--gutter) 6rem; }}
  .guide h1 {{ font-family: var(--display-font); font-size: 1.75rem; color: var(--heading); line-height: 1.35; }}
  .guide h2 {{ margin-top: 4rem; font-size: 1.5rem; color: var(--heading);
              padding-bottom: .75rem; border-bottom: 1px solid var(--border); }}
  .guide h3 {{ margin-top: 2rem; font-size: .8125rem; color: var(--muted);
              font-family: var(--ui-font); text-transform: uppercase; letter-spacing: .13em; }}
  .guide p  {{ color: var(--body); max-width: 62ch; margin-top: .75rem; }}
  .sws {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(13rem, 1fr));
         gap: .75rem; margin-top: 1rem; }}
  .sw {{ border-radius: var(--r-md); padding: 1rem; min-height: 6.5rem;
        display: grid; align-content: end; gap: .1875rem;
        border: 1px solid var(--border); }}
  .sw__n {{ font-family: var(--ui-font); font-weight: 600; font-size: .8125rem; }}
  .sw__h {{ font-family: var(--mono); font-size: .6875rem; opacity: .85; }}
  .sw__c {{ font-family: var(--mono); font-size: .625rem; opacity: .7; }}
  .specimen {{ margin-top: 1rem; padding: 1.5rem; background: var(--surface);
              border: 1px solid var(--border); border-radius: var(--r-md); }}
  .stage {{ margin-top: 1rem; padding: 2.5rem 1.5rem; border-radius: var(--r-lg);
           background: linear-gradient(180deg, var(--ground-2), var(--ground)); }}
  .row2 {{ display: flex; gap: .75rem; flex-wrap: wrap; align-items: center; margin-top: 1rem; }}
  .note {{ font-family: var(--mono); font-size: .6875rem; color: var(--muted);
          text-transform: uppercase; letter-spacing: .1em; margin-top: 1.5rem; }}
</style>
</head>
<body>
<main class="guide">

  <h1>Vivencia style guide</h1>
  <p>Generated from <code>styles.css</code> — swatches, hexes and contrast ratios are
     read out of the stylesheet, so this page cannot drift from the site. Regenerate
     with <code>./deploy/make-styleguide.py</code>.</p>

  <h2>Colour</h2>
  {groups}

  <h2>Type</h2>
  <div class="specimen">
    <div style="font-family:var(--display-font);font-size:2rem;line-height:1.32;color:var(--heading)">Michroma — hero headings</div>
    <div style="font-family:var(--ui-font);font-weight:600;font-size:1.5rem;margin-top:1.25rem;color:var(--heading)">Space Grotesk — headings, buttons, labels</div>
    <div style="font-family:var(--font);font-size:1.0625rem;margin-top:1.25rem;color:var(--body)">Inter — body copy. Everything read in sentences is set in this face, because the job of body type is to disappear.</div>
    <div style="font-family:var(--mono);font-size:.8125rem;margin-top:1.25rem;color:var(--muted)">IBM PLEX MONO — DATA INSIDE PRODUCT PANELS</div>
  </div>

  <h2>Components on light</h2>
  <div class="row2">
    <a class="btn btn--primary" href="#">Primary action</a>
    <a class="btn btn--ghost" href="#">Secondary</a>
    <span class="tag tag--ok">ok</span>
    <span class="tag tag--info">info</span>
    <span class="tag tag--calm">calm</span>
    <span class="tag tag--muted">muted</span>
  </div>

  <h2>Components on dark</h2>
  <div class="stage">
    <div style="font-family:var(--display-font);font-size:1.5rem;line-height:1.32;color:var(--on-ground-hi)">Statement in near-white.
      <span class="hero__accent">Payoff in gradient.</span></div>
    <p style="color:var(--on-ground-2);max-width:48ch">Supporting paragraph on a dark stage, set in the on-ground ramp.</p>
    <div class="row2">
      <a class="btn btn--primary" href="#">Primary</a>
      <a class="btn btn--ghost" href="#" style="background:rgba(36,107,253,.12);border-color:rgba(114,164,255,.42);color:var(--on-ground)">Outline</a>
    </div>
  </div>

  <p class="note">Not linked from the site · noindex</p>
</main>
</body>
</html>
'''
(root / 'styleguide.html').write_text(doc)
print(f'styleguide.html written — {len(tokens)} tokens read from styles.css')
