---
name: pptagent
description: Create and revise editable PowerPoint presentations from a brief using HTML slide sources, rendering, and visual review. Use when the requested deliverable is a PPTX deck. The host authors the slides; text-only hosts can use an external visual reviewer.
---

# PPTAgent

Use the host agent to research and author slides. The CLI handles rendering,
editable conversion, and verification that the delivered PPTX matches the
reviewed sources. Do not start another authoring agent.

## Setup

Resolve `SKILL_ROOT` to this directory. This project's shared Codex / Kimi Code
installation uses the launcher `bin/pptagent` at the project root (three
directories above this skill). Set `PPTAGENT_CLI` to its absolute path. Use the
launcher for every CLI command, including commands shown with direct Python
invocation in upstream references. It selects the installed Python, project-local
LibreOffice, and platform-specific Chromium. Native dependencies live under
`.runtime/linux-x86_64/`, `.runtime/linux-arm64/`, or `.runtime/macos-arm64/`;
never reuse a virtual environment or node_modules from a different platform.
Read `<project-root>/DEPLOYMENT.md` for installation and client usage. Run:

```bash
"$PPTAGENT_CLI" doctor --workspace "$PWD"
```

Read [references/task-contract.md](references/task-contract.md) for file layout
and HTML conversion constraints. The default `mode: multimodal` uses the host's
image viewer. Only for `mode: text`, read [references/text.md](references/text.md).
When `review_slides` and `review_deck` MCP tools are available in text mode, use
them for the corresponding review steps. Configuration is optional; defaults
live in `config.example.yaml`.

## Create or revise

For presentations using this project's concise business style, first apply the
companion [concise-business-ppt-style](../concise-business-ppt-style/SKILL.md).
It defines single-line summaries, a restrained palette, typography, visual
evidence, and the latest-user-file workflow. Its font preferences override the
generic platform font defaults below; current user instructions and hand-edited
sources take precedence. This is a local style specialization, not an upstream
PPTAgent mandate for unrelated decks.

- Resolve the user's audience, message, page count, language, and aspect ratio.
  On macOS, use `font-family: "Heiti SC", Arial, sans-serif` for Chinese
  slides. Linux uses `font-family: "Noto Sans CJK SC", "WenQuanYi Zen Hei", Arial, sans-serif`.
  Keep both platforms in a shared font fallback stack. The macOS LibreOffice
  has the matching system CJK fonts linked;
  check Chinese glyphs in the exported deck as well as the HTML render.
  For a new workspace, run `init --workspace "$PWD" --slides N`, with optional
  `--aspect-ratio 16:9|4:3|A1` and `--language`. Existing tasks use `task.json`.
- Use available research tools as needed and preserve sources for checkable
  claims. A manuscript or asset manifest is useful for complex decks, not a
  prerequisite for every edit.
- Use `scaffold` if starter HTML is useful; it preserves existing slides.
  Author exactly the requested page count and replace the starter text.
- Before the final visual review/build, apply the project's
  [Humanizer-zh skill](../humanizer-zh/SKILL.md) to Chinese slide copy and
  speaker notes, as requested by the user. Follow the final copy review below.
- Run `review-slides`, inspect every returned image, then record each result:

```bash
"$PPTAGENT_CLI" record-slide-review --workspace "$PWD" --slide slides/slide01.html --verdict pass --summary "Readable; no clipping, overlap, or broken images."
```

- Run `build`, then `review-deck`. Inspect the exported deck's contact sheets;
  open full-size pages for dense content. Record `record-deck-review` with
  `--verdict` and `--summary`. Text mode records visual results automatically.
- Fix issues that affect the user's requirements or visible quality. Source
  changes require fresh renders, reviews, and a build. Shared resource changes
  invalidate all slide reviews. Rendering alone does not establish a pass.
- Run `finalize`. Deliver `answer.pptx` only when `complete=true`. If the user
  explicitly accepts an incomplete draft, set `delivery.mode: best-effort`;
  `delivery_ready=true` then permits delivery with the failed checks disclosed.

Commands take `--workspace` with an absolute path and emit JSON. Use `--help`
for arguments. A successful delivery includes a current `final-report.json`.
Keep API keys in environment variables or the skill's `.env`, outside artifacts.

## Final Chinese copy review (Humanizer-zh)

Use Humanizer-zh as the last editorial pass for this project's PPTAgent decks,
including revisions. Review slide titles, body text, diagram labels, speaker
notes, and any accompanying speaking script. Keep the concise, professional
tone of a technical presentation; remove empty praise, repetition, and awkward
template phrasing only where they actually interfere with meaning.

Preserve facts, numbers, units, formulas, technical names, citations, personal
contribution boundaries, and qualifiers such as planned, unverified, or pending
evidence. Do not invent results or turn a proposed architecture into an implemented
one. Slide headings and labels may be polished within the deck-editing task;
preserve slide order, navigation targets, and content structure unless requested.
Leave code, HTML/CSS structure, file paths, URLs, IDs, and data intact. For HTML
and JSON speaker notes, edit only the human-readable text values. If a generator
is the source of truth, update its copy as well so regeneration retains the edits.

After wording changes, render the affected slides again and check line breaks,
clipping, and text size. Shared notes/assets changes require fresh reviews of all
slides. Build and review the actual PPTX, then run `finalize` as usual. If later
edits change the copy, repeat the editorial check for that copy before final
visual validation. Do not rewrite the exported PPTX after the acceptance checks.
Mention completion briefly in delivery; do not append style scores or a lengthy
rewrite report unless the user asks.
