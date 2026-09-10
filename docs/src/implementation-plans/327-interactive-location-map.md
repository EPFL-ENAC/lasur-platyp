---
status: accepted
issue: 327
last_updated: 2026-09-10
summary: Backend aggregates workplaces + home→workplace H3 flows; admin map gets workplace tooltips, hover-to-preview / click-to-pin filtering and 3D deck.gl arcs on a pitched MapLibre map.
---

# #327 — Interactive location map

## Problem

The admin chart "Geographical distribution of home and workplace locations"
(`admin/src/components/charts/LocationChart.vue` → `admin/src/components/LocationHeatmap.vue`)
rendered H3 res-8 hexagons of participant homes and red dots for workplaces with no
interactivity, while its description already promised click-to-filter behaviour.
The backend shipped workplaces as deduplicated `{lat, lon}` and no origin→destination data.

## Decisions (2026-09-10)

- **Backend is the source of truth for the aggregate.** `/stats/all` and `/stats/compare`
  now return workplace identity and the hex↔workplace flow counts; the frontend only
  filters and renders that aggregate.
- **Interaction model: hover previews, click pins.** Hovering a workplace shows a tooltip
  (name, campaigns with company names, participant count) and draws arcs to every home
  hexagon whose participants work there, hiding unrelated hexagons and workplaces. Hovering a
  hexagon does the symmetric thing. Clicking pins the preview so it survives mouse movement;
  clicking the same feature, empty map, Escape, or the reset button unpins. The cursor is a
  pointer over both workplaces and hexagons. (A click-only variant was tried on 2026-09-10
  and the hover preview was reinstated the same day.)
- **Flows are 3D deck.gl arcs** (`@deck.gl/layers` `ArcLayer` through `@deck.gl/mapbox`
  `MapboxOverlay` in overlaid mode, i.e. on deck.gl's own canvas above the map) on a MapLibre
  map pitched at 30°, width scaled by `sqrt(count)`, coloured from the home hexagon's own
  heatmap colour to the workplace red.
  MapLibre 5.x cannot elevate line layers, so a flat bezier line was tried first and replaced
  on 2026-09-10 at the user's request for a 3D look. Interleaved mode was tried and dropped:
  its view state only refreshes on map `move`, so the arcs drifted after the fullscreen resize.
  Overlaid mode re-syncs on every map `render`. The PNG export composites deck.gl's canvas
  (whose drawing buffer is preserved by default) over MapLibre's.
- **No per-flow privacy threshold.** Hexagons with a single household were already shown;
  the global `PRIVACY_LIMIT = 5` on the dataset is unchanged.
- The unused `Stats.workplace_location_heatmap` / `compute_workplace_location_heatmap` were
  deleted.

## Data shapes

```json
"workplace_locations": [
  {"id": 0, "lat": 46.5191, "lon": 6.5668, "name": "EPFL", "address": "Route Cantonale",
   "count": 12, "campaign_ids": [3, 7],
   "campaigns": [{"id": 3, "name": "Printemps 2026", "company_name": "EPFL"}]}
],
"home_workplace_flows": [{"hex_id": "881f8d4a3bfffff", "workplace_id": 0, "count": 3}]
```

`id` is the stable index of the workplace in the list (sorted by `(lat, lon)`).
`hex_id` uses the same H3 resolution (8) and helper as `home_location_heatmap`, so ids match.

## Implementation

Backend
- `api/models/query.py`: `WorkplaceCampaign`, `WorkplaceLocation`, `HomeWorkplaceFlow`;
  `Stats.workplace_locations` typed, `Stats.home_workplace_flows` added.
- `api/services/stats/locations.py`: `compute_workplaces()` groups records by workplace
  coordinates (first non-null name/address, count, sorted unique campaign ids) and counts
  flows per `(origin hexagon, workplace)`; rows without origin count toward the workplace but
  produce no flow. `attach_campaigns()` resolves ids to names and raises on a missing campaign.
- `api/services/campaigns.py`: `list_with_company(ids, user, special_permissions)` — one query
  with `Campaign.company` loaded, permission-filtered.
- `api/views/stats.py`: `enrich_workplaces()` runs once per request (union of campaign ids)
  for both `/stats/all` and `/stats/compare`.
- Tests: `tests/test_locations.py`.

Frontend (admin)
- `src/models.ts`, `src/stores/stats.ts`: new types, `homeWorkplaceFlows` state (also in the
  IndexedDB report snapshot).
- `src/utils/flows.ts`: pure helpers — `selectFlows`, `visibleIds`, `idFilter`, `makeFlowArcs`.
- `src/composables/useMapSelection.ts`: hover/click/Escape wiring, `pinned`/`hovered` state,
  MapLibre `setFilter` / `setPaintProperty` for the base layers, and a deck.gl `MapboxOverlay`
  whose `ArcLayer` is rebuilt from the selected flows; tooltip built with `textContent`.
- `src/components/LocationHeatmap.vue`: `hexId` / workplace `id` in feature properties, map
  pitched at 30° (kept through `fitBounds`), `interactive` prop (off in the report preview, so
  no deck.gl overlay there), reset button, popup closed before PNG export.
- `src/components/charts/LocationChart.vue`: new props, flow legend entry, reset button excluded
  from the export capture.
- i18n `stats.locations_heatmap.{flows, participants, unnamed_workplace, reset_selection,
  description}` in `en` and `fr`.

## Edge cases

- Same coordinates with different names: one dot, first non-null name, all campaign ids kept.
- Workplace without any origin: counted, no flows; selecting it shows only the dot.
- Comparison mode: enriched by the same helper; the map is not rendered per group today.
- A campaign id missing from the lookup raises (500 by design, no silent hole).

## Verification

- Backend: `make test`, `make lint` in `backend/`.
- Frontend: `npx vue-tsc --noEmit`, `npm run lint` in `admin/`; manual check of hover /
  click / Escape / reset / filter change / PNG export / report preview.
