# ADR 0002 — SQLite local como caché de trabajo, Cookidoo como fuente de verdad

**Status:** Accepted  
**Date:** 2026-04-18  
**Branch:** feat/phases-1-4-refactor  
**Design doc:** docs/designs/2026-04-18-planificacion-semanal-discovery.md

---

## Context

Para el feature de planificación semanal, el sistema necesita leer recetas de la librería del usuario y el historial del calendario para proponer un plan de 5 días. El flujo es conversacional e iterativo — el usuario puede pedir cambios varias veces antes de aprobar.

Si cada paso de la conversación hace llamadas a la API de Cookidoo, la experiencia es lenta (latencia de red en cada iteración) y frágil (depende de conectividad).

## Decision

Arquitectura de dos capas:

- **Cookidoo** = fuente de verdad. Las recetas viven ahí (custom collections, calendar). Es donde el usuario ve y gestiona sus recetas en la app móvil.
- **SQLite local** (`~/.thermomix/recipes.db`) = caché de trabajo. El planning itera sobre datos locales. Rápido, offline, sin dependencia de red durante la conversación.

El sync se hace explícitamente via `sync_library` MCP tool, no de forma automática en cada request.

## Schema

```sql
CREATE TABLE recipes (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  source TEXT,          -- 'cookidoo_custom' | 'cookidoo_managed' | 'external'
  collection TEXT,
  last_cooked DATE,
  times_cooked INTEGER DEFAULT 0,
  family_rating INTEGER, -- 1-5, null si no valorada
  tags TEXT,             -- JSON array
  synced_at TIMESTAMP
);

CREATE TABLE weekly_plans (
  week_start DATE PRIMARY KEY,
  plan JSON NOT NULL,
  created_at TIMESTAMP,
  confirmed BOOLEAN DEFAULT FALSE
);
```

## Consequences

- Planning conversacional rápido (sin llamadas API en cada iteración).
- `sync_library` debe ejecutarse para que la DB local esté al día con Cookidoo.
- Si el usuario añade recetas directamente en la app de Cookidoo, no aparecen hasta el próximo sync.
- La DB local es un caché derivado — puede regenerarse desde Cookidoo en cualquier momento.

## Alternatives Considered

- **Sin DB local, todo via API en tiempo real:** descartado. Latencia inaceptable para iteración conversacional.
- **DB propia como fuente de verdad (sin Cookidoo):** descartado. Las recetas deben estar en Cookidoo para que la app móvil las muestre y el usuario las pueda buscar ahí.
- **Archivo JSON en vez de SQLite:** descartado para >100 recetas. SQLite tiene indexing nativo y mejor rendimiento para filtros (por rating, last_cooked, tags).
