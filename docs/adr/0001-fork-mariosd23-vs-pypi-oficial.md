# ADR 0001 — Usar fork Mariosd23/cookidoo-api en vez de PyPI oficial

**Status:** Accepted  
**Date:** 2026-04-06  
**Branch:** feat/phases-1-4-refactor

---

## Context

El paquete oficial `miaucl/cookidoo-api` (PyPI) no tiene `create_custom_recipe` ni `edit_custom_recipe`. Sin estos métodos no se pueden crear recetas desde el MCP server.

Existe PR #179 de `Mariosd23` contra `miaucl/cookidoo-api` que añade exactamente esos métodos. El fork de Mariosd23 tiene los métodos funcionando y es la base del PR.

## Decision

Usar el fork de Mariosd23 como dependencia directa via git:

```
cookidoo-api @ git+https://github.com/Mariosd23/cookidoo-api.git@main
```

## Consequences

- `create_custom_recipe` y `edit_custom_recipe` disponibles inmediatamente.
- Dependencia a un fork personal sin versión pinada — riesgo de cambios breaking si el fork cambia.
- Cuando PR #179 sea mergeado en `miaucl/cookidoo-api` **y** se publique una versión nueva en PyPI que incluya los métodos, migrar a `cookidoo-api>=X.Y.Z`.

## Criterio de migración a PyPI

No migrar solo por número de versión. Verificar que `Cookidoo` class tenga `create_custom_recipe` antes de cambiar:

```python
from cookidoo_api import Cookidoo
assert hasattr(Cookidoo, 'create_custom_recipe')
```

**Nota:** v0.17.0 salió el 1-abril-2026 pero el PR #179 no estaba incluido. La versión que habilita la migración es v0.18.0 o posterior.

## Alternatives Considered

- Implementar las llamadas HTTP manualmente sin el fork: descartado. El fork tiene 50+ líneas de lógica probada que no vale la pena reimplementar.
- Esperar a que el PR se mergee antes de construir: descartado. El fork es estable y los tests cubren el comportamiento.
