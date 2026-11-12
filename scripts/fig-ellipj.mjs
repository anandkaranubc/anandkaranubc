// Fig. 2 of the profile README: the Jacobi elliptic functions sn, cn and dn,
// evaluated with stdlib's `math/base/special/ellipj` and drawn in units of the
// quarter period K(m). The parameter m breathes slowly from 0 (sn is a sine)
// towards 1 (sn becomes tanh); the motion is CSS keyframes on the path `d`
// property, so it stops under prefers-reduced-motion and degrades to the
// m = 0.9 frame where the `d` property is unsupported.
// Writes assets/fig-ellipj-{light,dark}.svg, assets/fig-ellipj.svg (follows the OS
// colour scheme, for viewers that ignore <picture>) and a phone layout.
//   npm install --ignore-scripts && npm run fig
import { writeFileSync } from 'node:fs';
import ellipj from '@stdlib/math-base-special-ellipj';

const layouts = {
  desktop: { W: 960, H: 320, LEFT: 112, RIGHT: 104, TOP: 40, BOTTOM: 48, font: 24, lbl: 30, small: 19, stroke: 1.75, extras: true },
  phone:   { W: 480, H: 200, LEFT: 40, RIGHT: 54, TOP: 16, BOTTOM: 36, font: 19, lbl: 23, small: 16, stroke: 1.4, extras: false }
};
let W, H, LEFT, RIGHT, TOP, BOTTOM, L;
const N = 160;
const FRAMES = [0, 0.5, 0.8, 0.93, 0.98, 0.995]; // m at 0%, 20%, ... 100%
const STATIC = 0.9;                              // the frame shown without animation
const PERIOD = '28s';

// Quarter period K(m) = pi / (2 AGM(1, sqrt(1 - m))).
function K(m) {
  let a = 1, b = Math.sqrt(1 - m);
  while (Math.abs(a - b) > 1e-15) [a, b] = [(a + b) / 2, Math.sqrt(a * b)];
  return Math.PI / (2 * a);
}

const x = (t) => LEFT + (t / 4) * (W - LEFT - RIGHT);          // t = u / K, in [0, 4]
const y = (v) => TOP + ((1 - v) / 2) * (H - TOP - BOTTOM);
const f = (n) => n.toFixed(1);

function path(fn, m) {
  const k = K(m);
  let d = '';
  for (let i = 0; i <= N; i++) {
    const t = (4 * i) / N;
    d += (i ? ' L' : 'M') + f(x(t)) + ' ' + f(y(fn(t * k, m)));
  }
  return d;
}

const curves = ['sn', 'cn', 'dn'];

const palette = {
  light: { sn: '#1f2328', cn: '#a40e26', dn: '#57606a', axis: '#8c959f', text: '#57606a' },
  dark:  { sn: '#e6edf3', cn: '#ff7b72', dn: '#9198a1', axis: '#6e7681', text: '#9198a1' }
};

const pct = (i) => Math.round((100 * i) / (FRAMES.length - 1)) + '%';
let GAUGE_X, GAUGE_W = 150;

function svg(scheme, layoutName) {
  L = layouts[layoutName]; ({ W, H, LEFT, RIGHT, TOP, BOTTOM } = L); GAUGE_X = x(4) - GAUGE_W;
  const frames = FRAMES.map((m) => ({ m, sn: path(ellipj.sn, m), cn: path(ellipj.cn, m), dn: path(ellipj.dn, m), dnmin: Math.sqrt(1 - m) }));
  const still = { sn: path(ellipj.sn, STATIC), cn: path(ellipj.cn, STATIC), dn: path(ellipj.dn, STATIC), dnmin: Math.sqrt(1 - STATIC) };
  const rules = (c) => `.sn{stroke:${c.sn}}.cn{stroke:${c.cn}}.dn{stroke:${c.dn}}.axis line,.gauge line{stroke:${c.axis}}text{fill:${c.text}}.lbl.sn{fill:${c.sn}}.lbl.cn{fill:${c.cn}}.lbl.dn{fill:${c.dn}}.gauge .mark{stroke:${c.sn}}`;
  const colours = scheme === 'auto'
    ? `${rules(palette.light)}@media(prefers-color-scheme:dark){${rules(palette.dark)}}`
    : rules(palette[scheme]);
  const keyframes = curves.map((c) =>
    `@keyframes ${c}{${frames.map((fr, i) => `${pct(i)}{d:path("${fr[c]}")}`).join('')}}`).join('\n') +
    `\n@keyframes dnmin{${frames.map((fr, i) => `${pct(i)}{transform:translateY(${f(y(fr.dnmin) - y(still.dnmin))}px);opacity:${fr.dnmin > 0.8 ? 0 : 1}}`).join('')}}` +
    `\n@keyframes gauge{${frames.map((fr, i) => `${pct(i)}{transform:translateX(${f(GAUGE_W * fr.m)}px)}`).join('')}}`;
  const anim = `animation-duration:${PERIOD};animation-timing-function:ease-in-out;animation-iteration-count:infinite;animation-direction:alternate`;
  const ticks = [1, 2, 3, 4].map((k) =>
    `<line x1="${f(x(k))}" x2="${f(x(k))}" y1="${f(y(0))}" y2="${f(y(0) + 6)}"/>` +
    `<text x="${f(x(k))}" y="${f(y(0) + 30)}" text-anchor="middle">${k === 1 ? '' : k}<tspan font-style="italic">K</tspan></text>`
  ).join('');
  const yticks = [[1, '1'], [0, '0'], [-1, '−1']].map(([v, t]) =>
    `<line x1="${LEFT - 8}" x2="${LEFT}" y1="${f(y(v))}" y2="${f(y(v))}"/>` +
    `<text x="${LEFT - 13}" y="${f(y(v) + 8)}" text-anchor="end">${t}</text>`
  ).join('');
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-labelledby="t">
<title id="t">Jacobi elliptic functions sn, cn and dn over one period, with the parameter m moving slowly between 0 and 1</title>
<style>
path{fill:none;stroke-width:${L.stroke};stroke-linecap:round;stroke-linejoin:round}
.dn{stroke-width:${L.stroke - 0.25};stroke-dasharray:5 4}
.axis line,.gauge line{stroke-width:1}
text{font-family:ui-serif,"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;font-size:${L.font}px}
.lbl{font-size:${L.lbl}px;font-style:italic}
.small{font-size:${L.small}px}
${colours}
${keyframes}
.sn{animation-name:sn;${anim}}.cn{animation-name:cn;${anim}}.dn{animation-name:dn;${anim}}
.dnmin{animation-name:dnmin;${anim}}.gauge .mark{animation-name:gauge;${anim}}
@media(prefers-reduced-motion:reduce){.sn,.cn,.dn,.dnmin,.gauge .mark{animation:none}}
</style>
<g class="axis"><line x1="${LEFT}" x2="${f(x(4))}" y1="${f(y(0))}" y2="${f(y(0))}"/>${ticks}${yticks}</g>
${L.extras ? `<g class="dnmin"><line class="axis" x1="${LEFT - 8}" x2="${LEFT}" y1="${f(y(still.dnmin))}" y2="${f(y(still.dnmin))}" style="stroke:${palette[scheme === 'auto' ? 'light' : scheme].axis}"/><text class="small" x="${LEFT - 13}" y="${f(y(still.dnmin) + 7)}" text-anchor="end">√(1−<tspan font-style="italic">m</tspan>)</text></g>` : ''}
<path class="sn" d="${still.sn}"/>
<path class="cn" d="${still.cn}"/>
<path class="dn" d="${still.dn}"/>
<text class="lbl sn" x="${f(x(4) + L.lbl / 2)}" y="${f(y(0) + 10)}">sn</text>
<text class="lbl cn" x="${f(x(4) + L.lbl / 2)}" y="${f(y(1) + 10)}">cn</text>
<text class="lbl dn" x="${f(x(4) + L.lbl / 2)}" y="${f(y(1) + 10 + L.lbl + 2)}">dn</text>
${L.extras ? `<g class="gauge">
<text class="small" x="${f(GAUGE_X - 14)}" y="${f(TOP - 14)}" text-anchor="end"><tspan font-style="italic">m</tspan></text>
<line x1="${f(GAUGE_X)}" x2="${f(GAUGE_X + GAUGE_W)}" y1="${f(TOP - 20)}" y2="${f(TOP - 20)}"/>
<text class="small" x="${f(GAUGE_X)}" y="${f(TOP - 26)}" text-anchor="middle">0</text>
<text class="small" x="${f(GAUGE_X + GAUGE_W)}" y="${f(TOP - 26)}" text-anchor="middle">1</text>
<line class="mark" x1="${f(GAUGE_X)}" x2="${f(GAUGE_X)}" y1="${f(TOP - 26)}" y2="${f(TOP - 14)}" style="stroke-width:2;transform:translateX(${f(GAUGE_W * STATIC)}px)"/>
</g>` : ''}
</svg>
`;
}

writeFileSync('assets/fig-ellipj-light.svg', svg('light', 'desktop'));
writeFileSync('assets/fig-ellipj-dark.svg', svg('dark', 'desktop'));
writeFileSync('assets/fig-ellipj.svg', svg('auto', 'desktop'));
writeFileSync('assets/fig-ellipj-phone.svg', svg('auto', 'phone'));
console.log(`ellipj: ${FRAMES.length} frames of ${N} points, desktop and phone`);
