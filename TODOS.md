# TODOS

## Ready to Build

### confirm_plan implementation
**What:** MCP tool that writes a confirmed weekly meal plan to the Cookidoo calendar.
**Why:** Completes the planning loop — sync → plan → approve → write to calendar.
**Unblocked (2026-04-19):** API confirmed — `add_recipes_to_calendar(day: date, recipe_ids)` and `add_custom_recipes_to_calendar(day: date, recipe_ids)` both accept date. Return `CookidooCalendarDay`.
**Where to start:** `cookidoo_service.py` (add calendar write methods) + `server.py` (new tool). Source field in DB determines which API to call.

### browse_cookidoo_collections tool
**What:** MCP tool to browse Cookidoo managed collections (curated recipe catalogs) for recipe discovery.
**Why:** Enables discovery of new recipes within Cookidoo — Claude can present collections, chapters and recipes for exploration.
**Unblocked (2026-04-19):** CookidooChapter structure confirmed — `CookidooChapter(name, recipes=[CookidooChapterRecipe(id, name, total_time)])`. Full structure available.
**Where to start:** `server.py` (new tool calling `api.get_managed_collections()`, iterate `.chapters[].recipes`).

## Future Features

### Reorganización de colecciones en Cookidoo
**What:** Flujo asistido por Claude para reorganizar las colecciones propias en un esquema más claro (aprobadas / a probar / por categoría).
**Why:** Hoy hay 8 colecciones mezcladas: algunas son para planning (`Las probe y me gustaron`), otras son experimentales (`Quiero Probar`, `Quiero probar sin harina`, `Dulces - quiero probar`). La distinción es implícita y mental. A medida que crece la librería, mantener esto ordenado manualmente se complica.
**Propuesta:** Un nuevo MCP tool `reorganize_library` o un flujo en `/semana` que permita mover recetas entre colecciones conversacionalmente ("mueve esta receta de Quiero Probar a Las probe y me gustaron"). Requiere `add_recipes_to_custom_collection()` y `remove_recipes_from_custom_collection()` del fork.
**Depende de:** que las colecciones de planning y experimentales estén bien diferenciadas en `COOKIDOO_PLANNING_COLLECTIONS`.

## Technical Debt

### FastMCP lifespan context manager
**What:** Properly close `aiohttp.ClientSession` when the MCP server shuts down.
**Why:** Currently `CookidooService.login()` creates a `ClientSession` that is never explicitly closed. Each call to `connect_to_cookidoo` leaks the previous session. In a long-running server, this accumulates.
**How:** Use FastMCP 3.x's lifespan context manager (`@mcp.context`/lifespan). Initialize the `_AppState` (including session) on startup, close it on shutdown.
**Priority:** Low for local personal use; required before open-sourcing.
**Where:** `server.py` — replace module-level `_state` with lifespan-managed state. `cookidoo_service.py` — ensure `close()` is awaited.
