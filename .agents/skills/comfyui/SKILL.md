---
name: comfyui
description: Connect to a self-hosted ComfyUI service to inspect available nodes and models, prepare API workflows, queue image generation, and retrieve illustrations for documents and presentations.
---

# ComfyUI connector

This is the project's connector for the
[self-hosted ComfyUI API](https://docs.comfy.org/development/comfyui-server/comms_routes).
Resolve the project root three directories above this skill and use its absolute
`bin/illustration-services` path. This connector does not install a backend,
model weights, or custom nodes; those are selected when configuring the service.

```bash
<project-root>/bin/illustration-services comfyui doctor
<project-root>/bin/illustration-services comfyui schema --out outputs/figures/comfyui-nodes.json
```

If the service is not configured, explain the missing `COMFYUI_URL` setting in
`<project-root>/.env.illustrations`. The example configuration is at the project
root. A successful `doctor` confirms API availability, not model readiness.
These routes target a self-hosted instance. Comfy Cloud uses its own API and
authentication; consult its current official API if the user chooses it.

## Prepare and execute a workflow

Inspect `/object_info` and `/models` (or model-specific folders) before selecting
node classes or checkpoints. Reuse a working API workflow supplied by the user
when available. A frontend graph with `nodes` and `links` is not a prompt API
payload; export the API version of the workflow first.

Write API-format node definitions to a task file, keyed by node ID, each with
`class_type` and `inputs`. Verify connections, node input names, image dimensions,
seed, and available model names against the service response.
Submit a JSON object containing `prompt: <node definitions>`:

```bash
<project-root>/bin/illustration-services comfyui request /prompt --method POST --json-file request.json --out submitted.json
```

Retain the returned `prompt_id`. Poll `/history/{prompt_id}` with a bounded
timeout, and inspect execution status and any validation or runtime errors.
Do not resubmit a timed-out POST until the queue or history establishes whether
it was accepted. Do not clear the shared queue or interrupt unrelated jobs.

For completed image outputs, use each entry's `filename`, `subfolder`, and `type`
to build a URL-encoded `/view` query. Download with
`request '/view?...' --out outputs/figures/image.png`. Keep workflow JSON and
the seed with the output so edits can reproduce the result.

Inspect the image at its intended slide size. Place labels in editable slide
text when exact wording matters. Copy selected images into the PPT task's
`assets/` folder, retain relative paths, and preserve transparent PNGs when the
workflow produced alpha. Describe only outputs that actually exist.
