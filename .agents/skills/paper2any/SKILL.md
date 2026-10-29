---
name: paper2any
description: Connect to a configured Paper2Any backend for paper-to-figure, editable research diagrams, and paper-to-slide workflows. Inspect the deployment's API schema before submitting jobs.
---

# Paper2Any connector

This project provides a local connector for the legacy open-source
[OpenDCAI/Paper2Any](https://github.com/OpenDCAI/Paper2Any) FastAPI service.
The backend and model services are configured separately; the hosted successor
Nexus Office is a different product. Do not claim a completed figure from a
prepared request or a disconnected backend.

Resolve the project root three directories above this skill. Use its absolute
`bin/illustration-services` path for commands. Start with:

```bash
<project-root>/bin/illustration-services paper2any doctor
```

If it reports `not_configured`, explain that this Skill is installed and needs
`PAPER2ANY_URL` plus any backend key in `<project-root>/.env.illustrations`.
Use `illustration-services.env.example` as the configuration guide. Preserve the
user's chosen model provider; choose required model services when setting up the
backend, rather than inventing working credentials.

## Use the deployed schema

Fetch the real API specification into the task output folder:

```bash
<project-root>/bin/illustration-services paper2any schema --out outputs/figures/paper2any-openapi.json
```

Find the route for the requested figure, diagram, or slide workflow and inspect
its request schema, security requirements, and response format. Follow `$ref`
links in `components.schemas`. Do not guess routes or assume a synchronous
endpoint when the service uses task IDs or streaming responses.

For an operation whose schema accepts JSON, write its payload to a local file
and use `request /verified/path --method POST --json-file payload.json --out response.json`.
For file uploads or SSE endpoints, use an appropriate multipart or streaming
client according to the fetched schema. Keep API keys in headers/environment.
The helper supports JSON bodies and binary downloads; it does not implement
multipart uploads or parse SSE streams.

Submit a generation job once. If the response is lost or times out, inspect the
service's task history before retrying. Follow its documented status endpoint,
report actual errors, and download completed output files into the task folder.
Inspect generated diagrams for incorrect claims, illegible labels, clipping,
and missing arrows. Preserve editable outputs such as SVG, DrawIO, and PPTX.

For a PPT, copy chosen assets into that task's `assets/` folder and use local
relative paths. A PNG inserted into PPT remains a raster image; retain the
editable source alongside it. Deliver only artifacts that were actually produced.
