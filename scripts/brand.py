"""Builds the profile's images from sources in assets/src and assets/shots.

  python3 scripts/brand.py        (needs fontTools: pip install fonttools)

Outputs, each as -light, -dark and an OS-following fallback (the hero also as -phone-light/-dark/-phone):
  assets/hero*.svg            pixel portrait (it blinks), name in Gig Pixel, two lines, three dated stamps
  assets/plate-<project>*.svg a crop of a 2x site capture inside a pixel frame
  assets/frieze*.svg          sn(z) on the complex plane, phase quantised to two tones on the pixel grid
Sources: GigPixel.ttf and the goblin are copied from the git-into-gsoc and gitgoblin repos;
portrait.txt is the 14x20 sprite (one character per pixel); shots/ are Playwright captures of
the live sites at 2880x1440 (PNG8 for flat pages, centre-cropped JPEG for photographic ones).
Needs fontTools and mpmath.
"""
import base64, cmath, math, re
import mpmath as mp
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = Path(__file__).resolve().parent.parent
SRC, SHOTS, OUT = ROOT / 'assets/src', ROOT / 'assets/shots', ROOT / 'assets'

FONT = TTFont(SRC / 'GigPixel.ttf')
CMAP, GLYPHS, UPEM = FONT.getBestCmap(), FONT.getGlyphSet(), FONT['head'].unitsPerEm

def text(s, size, x=0, y=0, cls='fg'):
    """Gig Pixel text as paths (the font is lowercase only; the brand retypes nothing)."""
    k, cx, parts = size / UPEM, 0, []
    for ch in s.lower():
        g = GLYPHS[CMAP[ord(ch)]]
        pen = SVGPathPen(GLYPHS); g.draw(pen); d = pen.getCommands()
        if d: parts.append(f'<path transform="translate({x + cx * k:.2f} {y}) scale({k:.5f} {-k:.5f})" d="{d}"/>')
        cx += g.width
    return f'<g class="{cls}">{"".join(parts)}</g>'

def width(s, size):
    return sum(GLYPHS[CMAP[ord(c)]].width for c in s.lower()) * size / UPEM

PORTRAIT = {'h': '#1b1512', 'H': '#3b312c', 's': '#e0b083', 'e': '#1b1512', 'b': '#3a2a22',
            'm': '#8a4a3a', 'W': '#f4f1fa', 't': '#d23b3b', 'w': '#f4f1fa', 'n': '#c48a5c'}
def portrait(x, y, px):
    """The sprite. Two lid layers with coprime periods close the eyes for about 150 ms at
    irregular intervals; both stop under prefers-reduced-motion."""
    rows = (SRC / 'portrait.txt').read_text().split('\n')
    cells, lids = [], []
    for cy, row in enumerate(rows):
        for cx, ch in enumerate(row):
            if ch in PORTRAIT:
                cells.append(f'<rect x="{x + cx * px}" y="{y + cy * px}" width="{px}" height="{px}" fill="{PORTRAIT[ch]}"/>')
            if ch == 'e':
                lids.append(f'<rect x="{x + cx * px}" y="{y + cy * px}" width="{px}" height="{px}" fill="{PORTRAIT["n"]}"/>')
    return (f'<g shape-rendering="crispEdges">{"".join(cells)}'
            f'<g class="lid a">{"".join(lids)}</g><g class="lid b">{"".join(lids)}</g></g>')

BLINK = ('@keyframes blink{0%,97.4%{opacity:0}97.5%,99.4%{opacity:1}99.5%,100%{opacity:0}}'
         '.lid{opacity:0}.lid.a{animation:blink 7.3s step-end infinite}.lid.b{animation:blink 11.1s step-end -4s infinite}'
         '@media(prefers-reduced-motion:reduce){.lid{animation:none}}')

def inner(svg_path):
    s = (SRC / svg_path).read_text()
    return re.sub(r'<title>.*?</title>', '', re.sub(r'^[\s\S]*?<svg[^>]*>', '', s).replace('</svg>', ''), flags=re.S).strip()

# Palette: git-into-gsoc's tokens. "merge" violet means merged in his system and stays violet
# in both schemes (the lighter merge-soft on dark, as the tokens prescribe for ink surfaces).
INK, PAPER, MERGE, MERGE_SOFT, MUTE_L, MUTE_D = '#15121E', '#F4F1FA', '#7A5AF8', '#C2B5FF', '#67607A', '#A49DB4'
T = {'light': dict(fg=INK, mute=MUTE_L, stamp=MERGE, frame=INK),
     'dark':  dict(fg=PAPER, mute=MUTE_D, stamp=MERGE_SOFT, frame=PAPER)}

def rules(c):
    return f'.fg{{fill:{c["fg"]}}}.mute{{fill:{c["mute"]}}}.stamp{{fill:{c["stamp"]}}}.frame{{fill:{c["frame"]}}}'

def style(scheme, extra=''):
    css = rules(T['light']) + '@media(prefers-color-scheme:dark){' + rules(T['dark']) + '}' if scheme == 'auto' else rules(T[scheme])
    return f'<style>{css}{extra}</style>'

def fit(txt, size, room):
    return min(size, room / width(txt, 1))

def stamp(x, y, scale, angle, lines, cls='stamp'):
    """A passport-style stamp like git-into-gsoc's: double outline, a little rotated, dated.
    lines = (big, mid, small); text sizes shrink to fit the box."""
    w, h = 296, 128
    big, mid, small = lines
    sb, sm, ss = fit(big, 44, w - 40), fit(mid, 20, w - 40), fit(small, 16, w - 40)
    body = (f'<rect x="0" y="0" width="{w}" height="{h}" rx="10" fill="none" stroke="currentColor" stroke-width="5"/>'
            f'<rect x="9" y="9" width="{w - 18}" height="{h - 18}" rx="6" fill="none" stroke="currentColor" stroke-width="2"/>'
            f'{text(big, sb, (w - width(big, sb)) / 2, 56, "cc")}'
            f'{text(mid, sm, (w - width(mid, sm)) / 2, 86, "cc")}'
            f'{text(small, ss, (w - width(small, ss)) / 2, 110, "cc")}')
    return f'<g class="{cls}" transform="translate({x} {y}) scale({scale}) rotate({angle} {w / 2} {h / 2})">{body}</g>'

STAMPS = [
    ('merged.', '580 pull requests into stdlib', 'dec 2024 to date', 'stamp-merge'),
    ('gsoc 2025.', 'special functions in js and c', 'google summer of code, stdlib', 'stamp-ink'),
    ('mlh fellowship.', 'openstack, python-ironicclient', 'spring 2026', 'stamp-ink'),
]
STAMP_CSS = '.cc{fill:currentColor}'

def hero(scheme, phone=False):
    lines = ['numerical kernels, open-source doors,', 'calculus on paper. cs and math at ubc.']
    m, g, f = STAMPS
    if not phone:
        W, H = 960, 300
        parts = [portrait(0, 14, 7),                                       # 98 x 140
                 text('karan anand', 84, 130, 102),
                 text(lines[0], 24, 130, 146, 'mute'), text(lines[1], 24, 130, 180, 'mute'),
                 stamp(724, -2, 0.7, 6, g[:3], g[3]),
                 stamp(578, 102, 1.0, -7, m[:3], m[3]),
                 stamp(704, 212, 0.64, -3, f[:3], f[3])]
    else:
        W, H = 480, 246
        parts = [portrait(0, 0, 5),                                        # 70 x 100
                 text('karan anand', 44, 90, 58),
                 text(lines[0], 15, 90, 86, 'mute'), text(lines[1], 15, 90, 108, 'mute'),
                 stamp(190, 134, 0.5, 5, g[:3], g[3]),
                 stamp(4, 150, 0.62, -6, m[:3], m[3]),
                 stamp(326, 154, 0.49, -3, f[:3], f[3])]
    def colours(c): return f'.stamp-merge{{color:{c["stamp"]}}}.stamp-ink{{color:{c["fg"]};opacity:0.82}}'
    extra = STAMP_CSS + BLINK + (f'{colours(T["light"])}@media(prefers-color-scheme:dark){{{colours(T["dark"])}}}'
                                 if scheme == 'auto' else colours(T[scheme]))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">'
            f'<title id="t">karan anand. numerical kernels, open-source doors, calculus on paper. cs and math at ubc. '
            f'three stamps: merged, 580 pull requests into stdlib, december 2024 to date; gsoc 2025, special functions in js and c; '
            f'mlh fellowship, openstack, spring 2026.</title>'
            f'{style(scheme, extra)}{"".join(parts)}</svg>\n')

def frieze(scheme):
    """sn(z) for m = 0.9 over three periods, phase quantised to eight sectors drawn in two tones
    on the pixel grid: a checkerboard the function warps around its zeros and poles."""
    M = 0.9
    K, Kp = float(mp.ellipk(M)), float(mp.ellipk(1 - M))
    cols, rows, px = 320, 64, 3
    sx, sy, y0 = 3 * 4 * K / cols, 2 * Kp / rows, -Kp / 2
    label = 'sn(z), m = 0.9'
    lw, lh = width(label, 16) + 20, 30
    on = []
    for j in range(rows):
        for i in range(cols):
            if i * px < lw and j * px > rows * px - lh: continue          # room for the label
            try: v = complex(mp.ellipfun('sn', mp.mpc((i + 0.5) * sx, y0 + (j + 0.5) * sy), m=M))
            except Exception: v = complex(1e9, 0)
            if int(((cmath.phase(v) + math.pi) / (2 * math.pi)) * 8) % 2 == 0:
                on.append(f'<rect x="{i * px}" y="{j * px}" width="{px}" height="{px}"/>')
    W, H = cols * px, rows * px
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">'
            f'<title id="t">The Jacobi elliptic function sn of a complex argument, m = 0.9, over three periods: its phase quantised to eight sectors and drawn as a two-tone pixel pattern that warps around the zeros and poles.</title>'
            f'{style(scheme, ".fz{opacity:0.4}")}<g class="fz mute" shape-rendering="crispEdges">{"".join(on)}</g>'
            f'{text(label, 16, 10, H - 9, "mute")}</svg>\n')

# Crops in 2x capture pixels (x, y, w, h); each plate's height follows its crop.
PLATES = {
    'git-into-gsoc': dict(crop=(0, 0, 2880, 960), mascot=''),
    'gitgoblin':     dict(crop=(0, 0, 1500, 1056),
                          mascot=f'<g transform="translate(1256 -128) scale(12)" shape-rendering="crispEdges">{inner("goblin-peek.svg")}</g>'),
    'longhand':      dict(crop=(0, 0, 1500, 1056), mascot=''),
    'erly':          dict(crop=(0, 0, 1040, 732), mascot='', pre=True),    # pre-cropped jpeg
    'whim':          dict(crop=(0, 0, 1500, 1056), mascot='', pre=True),
}

def plate(scheme, name):
    """A crop of the site capture inside a 4px frame with one-pixel notched corners.
    Light and dark use the site's own light and dark capture; the fallback carries both."""
    cx, cy, cw, ch = PLATES[name]['crop']
    B = 4
    W = 960 if cw == 2880 else 1508          # half plates share one width so they sit side by side
    k = (W - 2 * B) / cw                     # units per capture pixel
    H = round(ch * k) + 2 * B
    pre = PLATES[name].get('pre', False)
    def img(variant, cls=''):
        ext, mime = ('jpg', 'jpeg') if pre else ('png', 'png')
        data = base64.b64encode((SHOTS / f'{name}-{variant}.{ext}').read_bytes()).decode()
        # the capture, scaled so the crop fills the frame; the clip hides the rest
        iw, ih = (cw, ch) if pre else (2880, 1440)
        return (f'<image{cls} href="data:image/{mime};base64,{data}" x="{B - cx * k:.2f}" y="{B - cy * k:.2f}" '
                f'width="{iw * k:.2f}" height="{ih * k:.2f}" preserveAspectRatio="none"/>')
    images = img('light', ' class="l"') + img('dark', ' class="d"') if scheme == 'auto' else img('dark' if scheme == 'dark' else 'light')
    toggle = '.d{display:none}@media(prefers-color-scheme:dark){.l{display:none}.d{display:inline}}' if scheme == 'auto' else ''
    frame = (f'<g class="frame">'
             f'<rect x="{B}" y="0" width="{W - 2 * B}" height="{B}"/><rect x="{B}" y="{H - B}" width="{W - 2 * B}" height="{B}"/>'
             f'<rect x="0" y="{B}" width="{B}" height="{H - 2 * B}"/><rect x="{W - B}" y="{B}" width="{B}" height="{H - 2 * B}"/></g>')
    clip = f'<clipPath id="c"><rect x="{B}" y="{B}" width="{W - 2 * B}" height="{H - 2 * B}"/></clipPath>'
    top = 0 if W == 960 else 136          # the half plates share headroom so their frames align
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -{top} {W} {H + top}" width="{W}" height="{H + top}" role="img" aria-labelledby="t">'
            f'<title id="t">{name} website</title>{style(scheme, toggle)}<defs>{clip}</defs>'
            f'<g clip-path="url(#c)">{images}</g>{frame}{PLATES[name]["mascot"]}</svg>\n')

for scheme in ('light', 'dark', 'auto'):
    suffix = '' if scheme == 'auto' else f'-{scheme}'
    (OUT / f'hero{suffix}.svg').write_text(hero(scheme))
    (OUT / f'hero-phone{suffix}.svg').write_text(hero(scheme, phone=True))
    for name in PLATES:
        (OUT / f'plate-{name}{suffix}.svg').write_text(plate(scheme, name))
    (OUT / f'frieze{suffix}.svg').write_text(frieze(scheme))
print('wrote hero*.svg, plate-*.svg and frieze*.svg')
