# ADR 0003 — Fijar fastmcp >=3.0.0

**Status:** Accepted  
**Date:** 2026-04-18  
**Branch:** feat/phases-1-4-refactor

---

## Context

El proyecto fue iniciado con `fastmcp>=0.2.0` en `requirements.txt`. El paquete tuvo un salto de versión mayor (0.x → 2.x → 3.x) con cambios de API significativos. Con el constraint original, `uv pip install` resolvía a 3.x (la última versión compatible), lo cual funcionaba, pero el requirements.txt era engañoso — aceptaba versiones incompatibles.

Al investigar (2026-04-18): fastmcp 3.1.1 instalado, tests 43/43 pasan, las importaciones `FastMCP` y `fastmcp.prompts.Message` funcionan en 3.x.

## Decision

Actualizar constraint a `fastmcp>=3.0.0` en `requirements.txt`.

## Consequences

- El constraint refleja la realidad de lo que funciona.
- Un `uv sync` en un entorno limpio instalará 3.x, que es compatible.
- Si fastmcp 4.x introduce breaking changes en el futuro, el constraint no lo protege — evaluar cuando llegue.

## Alternatives Considered

- **Pin exacto `fastmcp==3.1.1`:** demasiado estricto para un proyecto en desarrollo activo.
- **Mantener `>=0.2.0`:** engañoso. Dice que cualquier versión desde 2022 funciona, lo cual no es cierto.
- **`>=3.0.0,<4.0.0`:** más defensivo. Válido si 4.x parece inminente o hay historial de breaking changes entre mayors. Evaluar en el futuro.
