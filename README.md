# SPIFFE / SPIRE Workload Identity Guide

Learning notes on workload identity for AI agents on OpenShift: SPIFFE and SPIRE, Zero Trust Workload Identity Manager, OpenShell token grants, Keycloak and the MCP Gateway.

**Site:** https://rcarrata.github.io/spiffe-spire-guide/

**Interactive version:** https://rcarrata.github.io/spiffe-spire-guide/modules/main/_attachments/spiffe-spire-explained.html

## Chapters

1. SPIFFE & SPIRE for dummies
2. Zero Trust Workload Identity Manager on OpenShift
3. Sandbox -> OpenShell Gateway -> Keycloak
4. JWT-SVID anatomy
5. Keycloak, OpenShell and SPIRE interactions
6. MCP Gateway integration

## Build locally

```bash
npm install
npx antora generate site.yml
open www/index.html
```

## Diagrams

Sources are `diagrams/*.excalidraw` (open in excalidraw.com). To regenerate them and the SVGs used by the pages:

```bash
python3 -I scripts/gen_excalidraw.py diagrams
python3 -I scripts/excalidraw_to_svg.py diagrams/*.excalidraw content/modules/ROOT/images
```

## Sources

Downloaded reference material lives in `sources/`, tracked in [sources/INDEX.md](sources/INDEX.md).

Not official documentation. Versions and status are as of 2026-11-20.
