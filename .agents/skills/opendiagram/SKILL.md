---
name: opendiagram
description: Create editable architecture, flow, sequence, and ER diagrams with the locally installed OpenDiagram layout engine, exporting Excalidraw, SVG, and PNG assets for PowerPoint.
---

# OpenDiagram for PPT assets

This is a project-authored integration skill, not an official upstream skill.
It uses the pinned [Itz-Agasta/OpenDiagram](https://github.com/Itz-Agasta/OpenDiagram)
engine and its Excalidraw conversion code. The AI authors semantic DiagramSpec
JSON; upstream code lays out and renders it. It does not deploy the OpenDiagram
website, database, account system, or its separate model service.

Resolve the project root three directories above this skill. Run
`<project-root>/bin/opendiagram doctor`; if missing, run
`bash <project-root>/scripts/setup-opendiagram.sh` after PPTAgent setup.
Runtime dependencies are separated by OS and CPU under `.runtime/`.

## Author and export

1. Read `references/spec-example.json` for a minimal input. For other diagram
   types or optional fields, inspect the pinned runtime's
   `opendiagram/harness/src/diagram-schema.ts` and `schema.ts`.
2. Write a local JSON file: `type`, `title`, `nodes` with unique `id` and `label`,
   and `edges` with existing `from` / `to` node IDs. Use `meta.direction` for flow
   direction. Keep actual project facts distinct from proposed architecture.
3. Run `<project-root>/bin/opendiagram render INPUT.json --out outputs/figures/NAME`.
   `--theme classic` is the default; `--theme sketch` uses the hand-drawn theme.
4. Inspect the actual PNG/SVG for readable labels, overlaps, arrows, and Chinese
   glyphs. Read `.report.json` warnings; successful execution is not visual review.
5. Preserve `.spec.json` and `.excalidraw` for editing. Copy SVG/PNG into the PPT
   task's `assets/`. PNG is static; native PowerPoint shapes are not promised.

The adapter supports upstream diagram types but does not bundle cloud icon
packs. Omit `icon`; use category and label instead. It rejects missing-node
edges and duplicate IDs before upstream sanitization can silently drop them.
External browser requests are blocked; dependencies and fonts are local.

For full browser-based collaborative editing, use a separately configured
OpenDiagram installation. Do not assume a local web service exists or guess
its API routes. This skill does not upload the user's project or call a model API.
