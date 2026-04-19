# ADR 0004 — Spec-driven development con gstack como metodología

**Status:** Accepted  
**Date:** 2026-04-18  
**Branch:** feat/phases-1-4-refactor

---

## Context

El proyecto usa Claude Code + gstack para el desarrollo. gstack genera documentación de diseño via `/office-hours` que se guarda en `~/.gstack/projects/` (local de la máquina, fuera del repo). Esto significa que las decisiones de diseño no están versionadas junto al código y se pierden entre sesiones o máquinas.

La industria converge hacia spec-driven development (SDD) para proyectos con AI coding: escribir la spec primero, luego implementar. GitHub publicó un toolkit open source para este patrón en 2025.

## Decision

Adoptar spec-driven development como metodología de trabajo:

1. **`/office-hours`** genera el design doc (spec) antes de implementar cualquier feature.
2. El design doc aprobado se copia a **`docs/designs/`** en el repo — esto es el spec.
3. Las decisiones arquitectónicas permanentes van a **`docs/adr/`** como ADRs numerados.
4. **`/plan-eng-review`** revisa el design doc antes de implementar.
5. Claude Code implementa basándose en el spec de `docs/designs/`.

## Estructura

```
docs/
  designs/          # Specs aprobados (output de /office-hours)
    YYYY-MM-DD-nombre-feature.md
  adr/              # Decisiones arquitectónicas permanentes
    0001-titulo.md
    0002-titulo.md
```

## Workflow por feature

```
Problema → /office-hours → design doc → aprobado → docs/designs/ → commit
                                                   ↓
                                          /plan-eng-review
                                                   ↓
                                          implementación
                                                   ↓
                                          /document-release (actualiza docs existentes)
```

## Instrucciones para gstack en cada iteración

- Antes de proponer implementación de cualquier feature: verificar si existe spec en `docs/designs/`.
- Al completar `/office-hours`: recordar copiar el design doc aprobado a `docs/designs/`.
- Al tomar una decisión arquitectónica importante (cambio de dependencia, cambio de patrón, nueva tecnología): crear un ADR en `docs/adr/` con el siguiente número disponible.
- `/plan-eng-review` debe leer los docs en `docs/designs/` además de los que encuentra en `~/.gstack/projects/`.

## Consequences

- Las specs y decisiones están versionadas junto al código — sobreviven cambios de máquina, onboarding de colaboradores, y paso del tiempo.
- Añade un paso de "copiar el design doc al repo" después de cada `/office-hours`. Vale la pena.
- Los ADRs capturan el "por qué" de decisiones que de otra forma se olvidan y se re-debaten.

## Alternatives Considered

- **Mantener docs solo en `~/.gstack/`:** descartado. Se pierden entre máquinas y no están versionados.
- **Solo CLAUDE.md:** insuficiente para specs detallados de features. CLAUDE.md es para contexto de proyecto, no para specs.
- **Notion/Confluence/etc.:** descartado. Fuera del flujo de git, se desincroniza del código.
