"""Builds the profile's images from sources in assets/src and assets/shots.

  python3 scripts/brand.py        (needs fontTools: pip install fonttools)

Outputs, each as -light, -dark, an OS-following fallback, and where noted a phone layout:
  assets/hero*.svg            pixel portrait, name in Gig Pixel, two lines, the merged stamp
  assets/plate-<project>*.svg a 2x screenshot inside a pixel frame, with the project's mascot
Sources: GigPixel.ttf and the marks are copied from the git-into-gsoc and gitgoblin repos;
portrait.txt is the 16x20 sprite (one character per pixel); shots/ are PNG8 captures of the live sites at 2880x1440, light and dark.
"""
import base64, re
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = Path(__file__).resolve().parent.parent
SRC, SHOTS, OUT = ROOT / 'assets/src', ROOT / 'assets/shots', ROOT / 'assets'

FONT = TTFont(SRC / 'GigPixel.ttf')
CMAP, GLYPHS, UPEM = FONT.getBestCmap(), FONT.getGlyphSet(), FONT['head'].unitsPerEm

def text(s, size, x=0, y=0, fill='currentColor'):
    """Gig Pixel text as paths (the font is lowercase only; the brand retypes nothing)."""
    k, cx, parts = size / UPEM, 0, []
    for ch in s.lower():
        g = GLYPHS[CMAP[ord(ch)]]
        pen = SVGPathPen(GLYPHS); g.draw(pen); d = pen.getCommands()
        if d: parts.append(f'<path transform="translate({x + cx * k:.2f} {y}) scale({k:.5f} {-k:.5f})" d="{d}"/>')
        cx += g.width
    attr = '' if fill == 'none' else f' fill="{fill}"'
    return cx * k, f'<g{attr}>{"".join(parts)}</g>'

def width(s, size):
    return sum(GLYPHS[CMAP[ord(c)]].width for c in s.lower()) * size / UPEM

PORTRAIT = {'h': '#1b1512', 's': '#dca772', 'e': '#1b1512', 'b': '#2a1f1a', 't': '#d23b3b', 'w': '#f4f1fa', 'n': '#b97d4f', 'm': '#8a4a3a'}
def portrait(x, y, px):
    rows = (SRC / 'portrait.txt').read_text().split('\n')
    cells = ''.join(f'<rect x="{x + cx * px}" y="{y + cy * px}" width="{px}" height="{px}" fill="{PORTRAIT[ch]}"/>'
                    for cy, row in enumerate(rows) for cx, ch in enumerate(row) if ch in PORTRAIT)
    return f'<g shape-rendering="crispEdges">{cells}</g>'

def inner(svg_path):
    s = (SRC / svg_path).read_text()
    return re.sub(r'<title>.*?</title>', '', re.sub(r'^[\s\S]*?<svg[^>]*>', '', s).replace('</svg>', ''), flags=re.S).strip()

# Palette: the git-into-gsoc tokens, which both brands share in spirit.
INK, PAPER, MERGE, OPEN, MUTE_L, MUTE_D = '#15121E', '#F4F1FA', '#7A5AF8', '#C6F432', '#67607A', '#A49DB4'
T = {'light': dict(fg=INK, mute=MUTE_L, stamp=MERGE, cursor=INK, frame=INK),
     'dark':  dict(fg=PAPER, mute=MUTE_D, stamp=OPEN, cursor=OPEN, frame=PAPER)}

def rules(c):
    return f'.fg{{fill:{c["fg"]}}}.mute{{fill:{c["mute"]}}}.stamp{{stroke:{c["stamp"]}}}.stamp-t{{fill:{c["stamp"]}}}.cursor{{fill:{c["cursor"]}}}.frame{{stroke:{c["frame"]}}}'

def style(scheme, extra=''):
    css = rules(T['light']) + '@media(prefers-color-scheme:dark){' + rules(T['dark']) + '}' if scheme == 'auto' else rules(T[scheme])
    return f'<style>{css}{extra}</style>'

def stamp(x, y, w, h, angle, lines, cls='stamp'):
    """A passport-style stamp like git-into-gsoc's: double outline, rotated a little."""
    big, small = lines
    bx, sx = x + (w - width(big, 44)) / 2, x + (w - width(small, 20)) / 2
    return (f'<g transform="rotate({angle} {x + w / 2} {y + h / 2})">'
            f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="none" stroke-width="5"/>'
            f'<rect class="{cls}" x="{x + 9}" y="{y + 9}" width="{w - 18}" height="{h - 18}" rx="6" fill="none" stroke-width="2"/>'
            f'<g class="stamp-t">{text(big, 44, bx, y + 58, "none")[1]}{text(small, 20, sx, y + h - 22, "none")[1]}</g></g>')


def hero(scheme, phone=False):
    if not phone:
        W, H = 960, 236
        parts = [portrait(0, 10, 7)]                                   # 112 x 140
        parts.append(text('karan anand', 84, 144, 96, 'none')[1].replace('<g>', '<g class="fg">', 1))
        for i, line in enumerate(['numerical kernels for stdlib.', 'tools that get people into open source.']):
            parts.append(text(line, 26, 144, 140 + i * 36, 'none')[1].replace('<g>', '<g class="mute">', 1))
        parts.append(stamp(660, 100, 296, 112, -7, ('merged.', '580 pull requests into stdlib')))
    else:
        W, H = 480, 330
        parts = [portrait(0, 0, 5)]                                    # 80 x 100
        parts.append(text('karan anand', 46, 100, 62, 'none')[1].replace('<g>', '<g class="fg">', 1))
        for i, line in enumerate(['numerical kernels for stdlib.', 'tools that get people into open source.']):
            parts.append(text(line, 19, 4, 138 + i * 28, 'none')[1].replace('<g>', '<g class="mute">', 1))
        parts.append(stamp(90, 204, 296, 112, -5, ('merged.', '580 pull requests into stdlib')))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">'
            f'<title id="t">karan anand. numerical kernels for stdlib. tools that get people into open source. stamp: merged, 580 pull requests into stdlib.</title>'
            f'{style(scheme)}{"".join(parts)}</svg>\n')

def plate(scheme, name, mascot):
    """A screenshot in a 4px pixel frame; the mascot sits on the frame's edge.
    Light and dark use the site's own light and dark capture; the fallback carries both."""
    W, H, B = 960, 484, 4
    def img(variant, cls=''):
        png = base64.b64encode((SHOTS / f'{name}-{variant}.png').read_bytes()).decode()
        return (f'<image{cls} href="data:image/png;base64,{png}" x="{B}" y="{B}" width="{W - 2 * B}" '
                f'height="{(W - 2 * B) / 2:.1f}" preserveAspectRatio="xMidYMin slice"/>')
    images = img('light', ' class="l"') + img('dark', ' class="d"') if scheme == 'auto' else img('dark' if scheme == 'dark' else 'light')
    toggle = '.d{display:none}@media(prefers-color-scheme:dark){.l{display:none}.d{display:inline}}' if scheme == 'auto' else ''
    frame = f'<rect class="frame" x="{B / 2}" y="{B / 2}" width="{W - B}" height="{H - B}" fill="none" stroke-width="{B}"/>'
    clip = f'<clipPath id="c"><rect x="{B}" y="{B}" width="{W - 2 * B}" height="{H - 2 * B}"/></clipPath>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -40 {W} {H + 40}" width="{W}" height="{H + 40}" role="img" aria-labelledby="t">'
            f'<title id="t">{name} website</title>{style(scheme, toggle)}<defs>{clip}</defs>'
            f'<g clip-path="url(#c)">{images}</g>{frame}{mascot}</svg>\n')

MASCOTS = {
    'gitgoblin': f'<g transform="translate(820 -36) scale(6)" shape-rendering="crispEdges">{inner("goblin-peek.svg")}</g>',
    'git-into-gsoc': None,  # set per scheme below: the mark's cursor is ink on light, lime on dark
    'longhand': '',
}

for scheme in ('light', 'dark', 'auto'):
    suffix = '' if scheme == 'auto' else f'-{scheme}'
    (OUT / f'hero{suffix}.svg').write_text(hero(scheme))
    for name in ('git-into-gsoc', 'gitgoblin', 'longhand'):
        m = MASCOTS[name]
        if m is None:
            m = f'<g transform="translate(866 -36) scale(3)" shape-rendering="crispEdges">{inner("gig-mark-" + ("dark" if scheme == "dark" else "light") + ".svg")}</g>'
        (OUT / f'plate-{name}{suffix}.svg').write_text(plate(scheme, name, m))
(OUT / 'hero-phone.svg').write_text(hero('auto', phone=True))
print('wrote hero*.svg and plate-*.svg')
