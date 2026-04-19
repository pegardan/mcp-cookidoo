# TODOS

## Blocked / Pending

### confirm_plan implementation
**What:** MCP tool that writes a confirmed weekly meal plan to the Cookidoo calendar.
**Why:** Completes the planning loop — sync → plan → approve → write to calendar.
**Blocked by:** Open Question #2 from the design doc: does `add_recipes_to_calendar(id, date)` accept a date parameter? If not, the tool needs a different approach.
**Context:** The Assignment (30-min API exploration with real Cookidoo account) resolves this. Run `get_recipes_in_calendar_week()` and `add_recipes_to_calendar()` with real credentials to see the actual API contract. See `docs/designs/2026-04-18-planificacion-semanal-discovery.md` §Open Questions #2.
**Where to start:** After The Assignment, check the API response shape, then implement in `server.py` and `cookidoo_service.py`.

### browse_cookidoo_collections tool
**What:** MCP tool to browse Cookidoo managed collections (curated recipe catalogs) for recipe discovery.
**Why:** Enables discovery of new recipes within Cookidoo — users can find well-rated public recipes to add to their personal library.
**Blocked by:** Open Question #1 from the design doc: what's inside `CookidooChapter`? Need to know the recipe list structure within a managed collection before the tool can be designed.
**Context:** Also part of The Assignment — call `get_managed_collections()` with real credentials, inspect the structure. See `docs/designs/2026-04-18-planificacion-semanal-discovery.md` §Open Questions #1.
**Where to start:** After The Assignment, check if `CookidooChapter` has recipe IDs/names. If yes, tool is straightforward. If not, alternative discovery flow needed.

## Technical Debt

### FastMCP lifespan context manager
**What:** Properly close `aiohttp.ClientSession` when the MCP server shuts down.
**Why:** Currently `CookidooService.login()` creates a `ClientSession` that is never explicitly closed. Each call to `connect_to_cookidoo` leaks the previous session. In a long-running server, this accumulates.
**How:** Use FastMCP 3.x's lifespan context manager (`@mcp.context`/lifespan). Initialize the `_AppState` (including session) on startup, close it on shutdown.
**Priority:** Low for local personal use; required before open-sourcing.
**Where:** `server.py` — replace module-level `_state` with lifespan-managed state. `cookidoo_service.py` — ensure `close()` is awaited.
