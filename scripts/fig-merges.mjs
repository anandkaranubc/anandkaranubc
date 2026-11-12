// Fig. 1 of the profile README: every pull request of mine merged into
// stdlib-js/stdlib, one hairline per merge, placed by merge date. Height and
// colour follow the commit type in the title: feat, fix, and everything else
// (bench, docs, test, refactor, chore, build, style). Overlaps darken, so ink
// density is merge density.
// Data: data/stdlib-merged.json, refreshed with
//   for p in 1 2 3 4 5 6 7; do gh api -X GET search/issues \
//     -f q='author:anandkaranubc is:pr is:merged repo:stdlib-js/stdlib' \
//     -f sort=created -f order=asc -f per_page=100 -f page=$p \
//     --jq '.items[] | {n: .number, t: .title, c: .created_at, m: .pull_request.merged_at}'; \
//   done | jq -s . > data/stdlib-merged.json
//   npm run fig
import { readFileSync, writeFileSync } from 'node:fs';

const prs = JSON.parse(readFileSync('data/stdlib-merged.json', 'utf8'));
const T0 = Date.UTC(2024, 11, 1), T1 = Date.UTC(2026, 11, 1); // Dec 2024 to Dec 2026
const kind = (title) => /^feat\b/.test(title) ? 'feat' : /^fix\b/.test(title) ? 'fix' : 'other';
const counts = { feat: 0, fix: 0, other: 0 };
for (const p of prs) counts[kind(p.t)]++;

const palette = {
  light: { feat: '#1f2328', fix: '#a40e26', other: '#6e7781', axis: '#8c959f', text: '#57606a', band: '#a40e26' },
  dark:  { feat: '#e6edf3', fix: '#ff7b72', other: '#8b949e', axis: '#6e7681', text: '#9198a1', band: '#ff7b72' }
};

// Two layouts: desktop (960 wide) and phone (480 wide, heavier strokes, larger type).
const layouts = {
  desktop: { W: 960, H: 196, LEFT: 24, RIGHT: 24, BASE: 128, top: 34, tall: 64, short: 30, stroke: 0.9, opacity: 0.85, font: 24, small: 21 },
  phone:   { W: 480, H: 176, LEFT: 12, RIGHT: 12, BASE: 118, top: 56, tall: 44, short: 20, stroke: 1.2, opacity: 0.9, font: 21, small: 18 }
};

function svg(scheme, layoutName) {
  const L = layouts[layoutName];
  const x = (iso) => L.LEFT + ((Date.parse(iso) - T0) / (T1 - T0)) * (L.W - L.LEFT - L.RIGHT);
  const f = (n) => n.toFixed(1);
  const height = { feat: L.tall, fix: L.tall, other: L.short };
  const line = (p) => `<line class="${kind(p.t)}" x1="${f(x(p.m))}" x2="${f(x(p.m))}" y1="${L.BASE}" y2="${L.BASE - height[kind(p.t)]}"/>`;
  // Fixes are drawn last so the few red lines sit on top of the many dark ones.
  const lines = prs.filter((p) => kind(p.t) !== 'fix').map(line).join('') + prs.filter((p) => kind(p.t) === 'fix').map(line).join('');

  const months = [];
  for (let d = new Date(T0); d.getTime() < T1; d.setUTCMonth(d.getUTCMonth() + 1)) months.push(new Date(d));
  const axis = months.map((d) => {
    const X = f(x(d.toISOString())), jan = d.getUTCMonth() === 0;
    return `<line x1="${X}" x2="${X}" y1="${L.BASE}" y2="${L.BASE + (jan ? 9 : 4)}"/>` +
      (jan ? `<text x="${X}" y="${L.BASE + L.font + 10}" text-anchor="middle">${d.getUTCFullYear()}</text>` : '');
  }).join('');

  // Google Summer of Code 2025, coding period (standard 12 weeks), as a band behind the lines.
  const g0 = x('2025-06-02'), g1 = x('2025-08-25');
  const band = `<rect class="band" x="${f(g0)}" y="${L.BASE - L.tall - 8}" width="${f(g1 - g0)}" height="${L.tall + 8}"/>` +
    `<text class="small" x="${f((g0 + g1) / 2)}" y="${L.BASE + L.font + 10}" text-anchor="middle">${layoutName === 'phone' ? 'GSoC 2025' : 'Google Summer of Code 2025'}</text>`;

  const key = `<tspan class="k feat">│</tspan> feat ${counts.feat}<tspan dx="12" class="k fix">│</tspan> fix ${counts.fix}<tspan dx="12" class="k other">│</tspan> other ${counts.other}`;
  const legend = layoutName === 'phone'
    ? `<text x="${L.LEFT}" y="${L.top - 34}"><tspan class="n">${prs.length}</tspan> merged pull requests</text><text class="small" x="${L.LEFT}" y="${L.top - 10}">${key}</text>`
    : `<text x="${L.LEFT}" y="${L.top - 10}"><tspan class="n">${prs.length}</tspan> merged pull requests<tspan class="small" dx="${L.font}">${key}</tspan></text>`;

  const rules = (c) => `.feat{stroke:${c.feat}}.fix{stroke:${c.fix}}.other{stroke:${c.other}}.axis line{stroke:${c.axis}}text{fill:${c.text}}.n{fill:${c.feat}}.k.feat{fill:${c.feat}}.k.fix{fill:${c.fix}}.k.other{fill:${c.other}}.band{fill:${c.band}}`;
  const colours = scheme === 'auto' ? `${rules(palette.light)}@media(prefers-color-scheme:dark){${rules(palette.dark)}}` : rules(palette[scheme]);
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${L.W} ${L.H}" width="${L.W}" height="${L.H}" role="img" aria-labelledby="t">
<title id="t">${prs.length} pull requests merged into stdlib between ${prs[0].m.slice(0, 10)} and ${prs[prs.length - 1].m.slice(0, 10)}, one line per merge on a time axis</title>
<style>
line{stroke-width:1}
.feat,.fix,.other{stroke-width:${L.stroke};opacity:${L.opacity}}
.fix{stroke-width:${L.stroke + 0.5};opacity:1}
.band{opacity:0.1}
text{font-family:ui-serif,"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;font-size:${L.font}px}
.small{font-size:${L.small}px}
.k{font-weight:bold}
${colours}
</style>
${band}
<g class="axis"><line x1="${L.LEFT}" x2="${L.W - L.RIGHT}" y1="${L.BASE}" y2="${L.BASE}"/>${axis}</g>
${legend}
${lines}
</svg>
`;
}

writeFileSync('assets/fig-merges-light.svg', svg('light', 'desktop'));
writeFileSync('assets/fig-merges-dark.svg', svg('dark', 'desktop'));
writeFileSync('assets/fig-merges.svg', svg('auto', 'desktop'));
writeFileSync('assets/fig-merges-phone.svg', svg('auto', 'phone'));
console.log(`merges: ${prs.length} (feat ${counts.feat}, fix ${counts.fix}, other ${counts.other})`);
