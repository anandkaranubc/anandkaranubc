// Draws Fig. 1 of the profile README: the Jacobi elliptic functions sn, cn
// and dn for m = 0.9, evaluated with stdlib's `math/base/special/ellipj`.
// Writes assets/fig1-light.svg, assets/fig1-dark.svg and assets/fig1.svg
// (the last one follows the OS colour scheme, for viewers that ignore <picture>).
//   npm install --ignore-scripts && npm run fig
import { writeFileSync } from 'node:fs';
import ellipj from '@stdlib/math-base-special-ellipj';

const M = 0.9;
const W = 960, H = 320, LEFT = 112, RIGHT = 104, TOP = 36, BOTTOM = 48;
const N = 480;

// Quarter period K(m): first zero of cn on (0, 4), by bisection.
let lo = 0, hi = 4;
for (let i = 0; i < 80; i++) { const mid = (lo + hi) / 2; (ellipj.cn(mid, M) > 0 ? lo = mid : hi = mid); }
const K = (lo + hi) / 2;
const UMAX = 4 * K;

const x = (u) => LEFT + (u / UMAX) * (W - LEFT - RIGHT);
const y = (v) => TOP + ((1 - v) / 2) * (H - TOP - BOTTOM);
const f = (n) => n.toFixed(2);

function path(fn) {
  let d = '';
  for (let i = 0; i <= N; i++) {
    const u = (UMAX * i) / N;
    d += (i ? ' L' : 'M') + f(x(u)) + ' ' + f(y(fn(u, M)));
  }
  return d;
}

const curves = [
  { id: 'sn', d: path(ellipj.sn), end: ellipj.sn(UMAX, M) },
  { id: 'cn', d: path(ellipj.cn), end: ellipj.cn(UMAX, M) },
  { id: 'dn', d: path(ellipj.dn), end: ellipj.dn(UMAX, M) }
];

const palette = {
  light: { sn: '#1f2328', cn: '#a40e26', dn: '#57606a', axis: '#8c959f', text: '#57606a' },
  dark:  { sn: '#e6edf3', cn: '#ff7b72', dn: '#9198a1', axis: '#6e7681', text: '#9198a1' }
};

function svg(scheme) {
  const p = palette[scheme];
  // Plain per-class rules rather than custom properties: librsvg and some
  // webviews ignore var(), and the figure must never render blank.
  const rules = (c) => `.sn{stroke:${c.sn}}.cn{stroke:${c.cn}}.dn{stroke:${c.dn}}.axis line{stroke:${c.axis}}text{fill:${c.text}}.lbl.sn{fill:${c.sn}}.lbl.cn{fill:${c.cn}}.lbl.dn{fill:${c.dn}}`;
  const media = scheme === 'auto'
    ? `${rules(palette.light)}@media(prefers-color-scheme:dark){${rules(palette.dark)}}`
    : rules(p);
  const ticks = [1, 2, 3, 4].map((k) =>
    `<line x1="${f(x(k * K))}" x2="${f(x(k * K))}" y1="${f(y(0))}" y2="${f(y(0) + 6)}"/>` +
    `<text x="${f(x(k * K))}" y="${f(y(0) + 30)}" text-anchor="middle">${k === 1 ? '' : k}<tspan font-style="italic">K</tspan></text>`
  ).join('');
  const yticks = [[1, '1'], [Math.sqrt(1 - M), '√(1−<tspan font-style="italic">m</tspan>)'], [0, '0'], [-1, '−1']].map(([v, t]) =>
    `<line x1="${LEFT - 8}" x2="${LEFT}" y1="${f(y(v))}" y2="${f(y(v))}"/>` +
    `<text x="${LEFT - 13}" y="${f(y(v) + 8)}" text-anchor="end"${v === 1 || v === 0 || v === -1 ? '' : ' font-size="19"'}>${t}</text>`
  ).join('');
  // Label positions: nudge apart when two curves end close together.
  const labels = curves.map((c) => ({ ...c, ly: y(c.end) })).sort((a, b) => a.ly - b.ly);
  for (let i = 1; i < labels.length; i++) if (labels[i].ly - labels[i - 1].ly < 32) labels[i].ly = labels[i - 1].ly + 32;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-labelledby="t">
<title id="t">Jacobi elliptic functions sn, cn and dn for m = ${M}, over one period 0 to 4K</title>
<style>
path{fill:none;stroke-width:1.75;stroke-linecap:round;stroke-linejoin:round}
.dn{stroke-width:1.5;stroke-dasharray:5 4}
.axis line{stroke-width:1}
text{font-family:ui-serif,"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;font-size:24px}
.lbl{font-size:30px;font-style:italic}
${media}
</style>
<g class="axis"><line x1="${LEFT}" x2="${f(x(UMAX))}" y1="${f(y(0))}" y2="${f(y(0))}"/>${ticks}${yticks}</g>
${curves.map((c) => `<path class="${c.id}" d="${c.d}"/>`).join('\n')}
${labels.map((c) => `<text class="lbl ${c.id}" x="${f(x(UMAX) + 30)}" y="${f(c.ly + 7)}">${c.id}</text>`).join('\n')}
<text x="${f(x(UMAX))}" y="${f(y(1) - 12)}" text-anchor="end"><tspan font-style="italic">m</tspan> = ${M}</text>
</svg>
`;
}

writeFileSync('assets/fig1-light.svg', svg('light'));
writeFileSync('assets/fig1-dark.svg', svg('dark'));
writeFileSync('assets/fig1.svg', svg('auto'));
console.log(`K(${M}) = ${K.toFixed(6)}; wrote assets/fig1-{light,dark}.svg and assets/fig1.svg`);
