// Merges each project's light and dark banner into one SVG that follows the
// OS colour scheme, used as the <img> fallback where <picture> is ignored.
import { readFileSync, writeFileSync } from 'node:fs';
for (const name of ['git-into-gsoc', 'gitgoblin']) {
  const inner = (s) => s.replace(/^[\s\S]*?<svg[^>]*>/, '').replace(/<\/svg>\s*$/, '');
  const light = readFileSync(`assets/marks/${name}-light.svg`, 'utf8');
  const dark = readFileSync(`assets/marks/${name}-dark.svg`, 'utf8');
  const open = light.match(/<svg[^>]*>/)[0];
  writeFileSync(`assets/marks/${name}.svg`,
    `${open}<style>.d{display:none}@media(prefers-color-scheme:dark){.l{display:none}.d{display:inline}}</style><g class="l">${inner(light)}</g><g class="d">${inner(dark)}</g></svg>\n`);
}
console.log('marks: wrote assets/marks/{git-into-gsoc,gitgoblin}.svg');
