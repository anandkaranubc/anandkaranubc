"""Builds the profile's images from sources in assets/src and assets/shots.

  python3 scripts/brand.py        (needs fontTools: pip install fonttools)

Outputs, each as -light, -dark and an OS-following fallback (the hero also as -phone-light/-dark/-phone):
  assets/hero*.svg            pixel portrait, name in Gig Pixel, two lines, the merged stamp
  assets/plate-<project>*.svg a crop of a 2x site capture inside a pixel frame
Sources: GigPixel.ttf and the goblin are copied from the git-into-gsoc and gitgoblin repos;
portrait.txt is the 14x20 sprite (one character per pixel); shots/ are PNG8 Playwright
captures of the live sites at 2880x1440, light and dark.
"""
import base64, re
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
    rows = (SRC / 'portrait.txt').read_text().split('\n')
    cells = ''.join(f'<rect x="{x + cx * px}" y="{y + cy * px}" width="{px}" height="{px}" fill="{PORTRAIT[ch]}"/>'
                    for cy, row in enumerate(rows) for cx, ch in enumerate(row) if ch in PORTRAIT)
    return f'<g shape-rendering="crispEdges">{cells}</g>'

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

def stamp(x, y, scale=1.0):
    """A passport-style stamp like git-into-gsoc's: double outline, a little rotated, dated."""
    w, h = 296, 128
    big, mid, date = 'merged.', '580 pull requests into stdlib', 'dec 2024 to date'
    body = (f'<rect class="stamp-o" x="0" y="0" width="{w}" height="{h}" rx="10" fill="none" stroke-width="5"/>'
            f'<rect class="stamp-o" x="9" y="9" width="{w - 18}" height="{h - 18}" rx="6" fill="none" stroke-width="2"/>'
            f'{text(big, 44, (w - width(big, 44)) / 2, 56, "stamp")}'
            f'{text(mid, 20, (w - width(mid, 20)) / 2, 86, "stamp")}'
            f'{text(date, 16, (w - width(date, 16)) / 2, 110, "stamp")}')
    return f'<g transform="translate({x} {y}) scale({scale}) rotate(-7 {w / 2} {h / 2})">{body}</g>'

STAMP_CSS = '.stamp-o{stroke:currentColor}'

def hero(scheme, phone=False):
    lines = ['numerical kernels for stdlib.', 'tools that get people into open source.']
    if not phone:
        W, H = 960, 252
        parts = [portrait(0, 8, 7),                                       # 98 x 140
                 text('karan anand', 84, 130, 96),
                 text(lines[0], 26, 130, 140, 'mute'), text(lines[1], 26, 130, 176, 'mute'),
                 stamp(652, 84)]
    else:
        W, H = 480, 262
        parts = [portrait(0, 0, 5),                                       # 70 x 100
                 text('karan anand', 44, 90, 58),
                 text(lines[0], 17, 90, 90, 'mute'), text(lines[1], 17, 90, 114, 'mute'),
                 stamp(94, 136, 0.68)]
    # the stamp outline takes the stamp colour through currentColor on its group
    svg = ''.join(parts).replace('<g transform="translate', '<g class="stamp-g" transform="translate', 1)
    extra = STAMP_CSS + (f'.stamp-g{{color:{T["light"]["stamp"]}}}@media(prefers-color-scheme:dark){{.stamp-g{{color:{T["dark"]["stamp"]}}}}}'
                         if scheme == 'auto' else f'.stamp-g{{color:{T[scheme]["stamp"]}}}')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">'
            f'<title id="t">karan anand. numerical kernels for stdlib. tools that get people into open source. '
            f'stamp: merged, 580 pull requests into stdlib, december 2024 to date.</title>'
            f'{style(scheme, extra)}{svg}</svg>\n')

# Crops in 2x capture pixels (x, y, w, h); each plate's height follows its crop.
PLATES = {
    'git-into-gsoc': dict(crop=(0, 0, 2880, 960), mascot=''),
    'gitgoblin':     dict(crop=(0, 0, 1500, 1056),
                          mascot=f'<g transform="translate(1256 -128) scale(12)" shape-rendering="crispEdges">{inner("goblin-peek.svg")}</g>'),
    'longhand':      dict(crop=(0, 0, 1500, 1056), mascot=''),
}

def plate(scheme, name):
    """A crop of the site capture inside a 4px frame with one-pixel notched corners.
    Light and dark use the site's own light and dark capture; the fallback carries both."""
    cx, cy, cw, ch = PLATES[name]['crop']
    B = 4
    W = 960 if cw == 2880 else 1508          # half plates share one scale: 1500 px of capture -> 1500 units
    k = (W - 2 * B) / cw                     # units per capture pixel
    H = round(ch * k) + 2 * B
    def img(variant, cls=''):
        png = base64.b64encode((SHOTS / f'{name}-{variant}.png').read_bytes()).decode()
        # the full capture, scaled so the crop fills the frame; the clip hides the rest
        return (f'<image{cls} href="data:image/png;base64,{png}" x="{B - cx * k:.2f}" y="{B - cy * k:.2f}" '
                f'width="{2880 * k:.2f}" height="{1440 * k:.2f}" preserveAspectRatio="none"/>')
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
print('wrote hero*.svg and plate-*.svg')
