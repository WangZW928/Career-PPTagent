import fs from 'node:fs';
import { createRequire } from 'node:module';
// Upstream targets Bun's global Worker. ELK's own in-process Worker is the
// supported Node fallback, with the same layout engine and message interface.
globalThis.Worker = createRequire(import.meta.url)('elkjs/lib/elk-worker.min.js').Worker;
const { diagramSpecSchema, layoutDiagram, renderToExcalidraw, renderSequenceDiagram, themes } = await import('./harness/src/index.js');
const [input, output, themeName = 'classic'] = process.argv.slice(2);
if (!input || !output || !['classic', 'sketch'].includes(themeName)) throw Error('layout input.json output.json [classic|sketch]');
const spec = diagramSpecSchema.parse(JSON.parse(fs.readFileSync(input, 'utf8')));
const ids = new Set(spec.nodes.map(n => n.id));
if (ids.size !== spec.nodes.length) throw Error('Duplicate node IDs');
for (const edge of spec.edges) if (!ids.has(edge.from) || !ids.has(edge.to)) throw Error('Edge references an unknown node');
const theme = themes[themeName];
// Icon packs are not bundled in this local adapter. Keep labels instead of silent missing icons.
if (spec.nodes.some(n => n.icon)) throw Error('Local adapter does not bundle icon packs; remove icon fields');
const placed = spec.type === 'sequence' ? null : await layoutDiagram(spec, theme);
const result = placed ? renderToExcalidraw(placed, {}, theme) : renderSequenceDiagram(spec, theme);
fs.writeFileSync(output, JSON.stringify({ ...result, warnings: placed?.warnings ?? result.warnings ?? [] }));
