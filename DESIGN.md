# Vivencia — design reference

The vibe, the layout and the rules each element follows. Colour values live in
`styles.css` as tokens; the live swatches with contrast ratios are generated at
`/styleguide.html` by `./deploy/make-styleguide.py`.

## Overall vibe

Premium enterprise sci-fi, built on restraint. The page reads as instrument
panel rather than brochure: cobalt on midnight, hairline structure, generous
negative space, and light used as the primary expressive device. Nothing is
decorative for its own sake — depth comes from **ground**, **glow** and
**typographic scale**, never from bevels, gloss or drop shadows.

The governing move is a **stage sandwich**. Dark sections are cinematic and
emissive; light sections are clean and readable. Long-form reading always
happens on light; every "moment" — the hero, the shared-modules claim, the
CTA — happens on dark, where colour can actually burn.

```
NAV            floating dark capsule, over everything
HERO           midnight · full screen · full-bleed rays · glass stats
SUITES         white · five chapters · centre spine · sticky panels
PLATFORM       ice · four cards
BACK OFFICE    midnight · 4x4 module matrix
FAQ            ice · single glass panel
CTA            midnight · concentrated bloom
FOOTER         midnight · artwork ground
```

## Arrangement

| | Value |
| --- | --- |
| Container | 1320px max, gutter `clamp(20px, 4vw, 72px)` |
| Section rhythm | `clamp(80px, 11vw, 140px)` vertical |
| Stage seam | 1px gradient hairline, fading out at 8% each end — a seam, never a border |
| Grid | Steps 2-col asymmetric `1fr / 1.05fr`; cards 4-col; modules 4x4; footer `1.8fr + 2x1fr` |
| Breakpoints | 1101px (steps stack, spine hides), 860px (sticky off), 720px (single column, drawer nav) |
| Radii | 8px small · 16px cards · 20px large · 24px panels · pill for actions |

## Element by element

**Nav** — 70rem pill capsule, 56px tall, sticky at 16px, pulled up `-3.5rem` so
it floats *in* the hero rather than above it. `rgba(7,21,47,.68)` glass, 22px
blur, cobalt hairline, deepening on scroll. Right-aligned links, then outline
and solid actions.

**Hero** — `100svh`, content grid-centred. Artwork sits full-bleed behind at
`inset: 0`, inverted and screened so the rays emit rather than absorb. Stack:
headline, paragraph, two CTAs, fine print, four glass stat tiles. The headline
splits two-tone — statement in near-white, payoff in the `#A8C6FF → #55D7FF`
gradient, because gradienting the whole sentence flattens the hierarchy.

**Step chapter** — text left, panel right, alternating each row. A centre
**spine** runs the section: dim track, lit fill following scroll, and a node per
chapter that ignites as it passes. The panel is **sticky** — it holds while its
description scrolls past. Inside: number chip, mono label, heading, lede, three
hairline-separated features, bordered pull-quote.

**Product panel** — 24px radius, 80% white, cobalt hairline, 20px blur, sitting
in its own pool of light. Titlebar with three dots and a mono path. Rows carry a
bold label, a meta line, and a right-aligned status tag.

**Cards** — 90% white, `#DEE8FA` border, 48px rounded icon tile, title, body.
Hover lifts 3px into a soft `rgba(16,42,140,.08)` shadow — elevated, not glossy.

**Module matrix** — sixteen equal cells, 4x4, left-aligned labels, caret space
reserved so nothing shifts on hover. Four highlighted in solid cobalt. The shape
states the count so the heading does not have to.

**FAQ** — one 52rem glass panel, rows separated by hairlines, `+`/`-` control in
a circular chip that fills cobalt when open.

**Footer** — the artwork itself is the ground, hue-rotated to cobalt, under two
scrims: vertical, so the page dissolves into it, and horizontal, darkening the
right where the link columns sit.

## Type

| Face | Role |
| --- | --- |
| **Michroma** | Hero and CTA headings only — one weight, very wide, tracking at zero, leading 1.32 |
| **Space Grotesk** | All other headings, buttons, nav, labels, figures |
| **Inter** | Everything read in sentences |
| **IBM Plex Mono** | Data inside product panels, so they read as an application |

Micro-labels are Space Grotesk, uppercase, `.13em` tracked. Michroma is rationed
to two headings: it is a single weight with no italic, and anything smaller set
in it stops being futuristic and becomes hard work.

## Colour system

Three grounds — white, ice `#F2F6FF`, midnight `#07152F`. Type is taken from
whichever ramp matches the ground:

- light stages `#0A1D42 / #435679 / #607294`
- dark stages `#F7FAFF / #C4D4F4 / #91A6CF`

`#1557E8` is the accent on light surfaces. `#246BFD / #4385FF / #72A4FF` are the
emissive set for dark ones, because the primary is too deep to glow against
midnight. The cyan endpoint `#55D7FF` is reserved for gradient stops and
illumination — it never becomes a second brand colour.

Every pair clears AA on the ground it actually sits on. Two to watch: `#607294`
on ice is 4.5:1, and white on `#246BFD` is 4.6:1 — so the lighter `#4385FF` must
stay a gradient stop rather than becoming a solid button fill.

## Motion

Everything is `transform`/`opacity` only, on `cubic-bezier(.16,1,.3,1)`.

- **Reveals** — 20px rise, staggered per group, fired once
- **Sticky panels** — hold through their description
- **Spine** — fill tracks the viewport midpoint, so the light sits where the eye is
- **Parallax** — 8px drift on panels, desktop only
- **Coordinate lock** — `[ ]` brackets fly in, overshoot 2px, lock; hairline sweeps under
- **Crop marks** — `+` at card and panel corners
- **Glow** — three tiers, dark stages only

All of it collapses under `prefers-reduced-motion` — except sticky, which is
layout, not decoration.

## Rules worth not breaking

1. **Glow only on dark.** On white it degrades to a coloured shadow; that is why
   the stages alternate at all.
2. **Never animate padding or width on hover.** Both reflow text. Reserve the
   space at rest and move the mark.
3. **Check contrast on the ground the colour actually sits on**, not against
   white by default.
4. **Do not add a colour outside the ramp.** The tag classes are named for state
   (`ok`, `info`, `calm`, `muted`), not for hue, so they cannot drift into a
   fifth colour.
