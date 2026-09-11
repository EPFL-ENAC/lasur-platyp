import { cellToLatLng } from 'h3-js'
import type { ExpressionSpecification, FilterSpecification, Map as MaplibreMap } from 'maplibre-gl'
import type { HomeWorkplaceFlow, WorkplaceLocation } from '@/models'
import { parseHex, type RGB } from '@/utils/colors'

export type MapSelection = { kind: 'workplace'; id: number } | { kind: 'hex'; id: string } | null

export function sameSelection(a: MapSelection, b: MapSelection): boolean {
  if (a === null || b === null) return a === b
  return a.kind === b.kind && a.id === b.id
}

/** Flows attached to the selected feature; the backend aggregate is only filtered here. */
export function selectFlows(
  flows: HomeWorkplaceFlow[],
  selection: MapSelection,
): HomeWorkplaceFlow[] {
  if (selection === null) return []
  if (selection.kind === 'workplace') return flows.filter((f) => f.workplace_id === selection.id)
  return flows.filter((f) => f.hex_id === selection.id)
}

/** Ids to keep visible; `null` on a side means "show everything". */
export function visibleIds(
  selected: HomeWorkplaceFlow[],
  selection: MapSelection,
): { hexIds: string[] | null; workplaceIds: number[] | null } {
  if (selection === null) return { hexIds: null, workplaceIds: null }
  if (selection.kind === 'workplace') {
    return { hexIds: selected.map((f) => f.hex_id), workplaceIds: [selection.id] }
  }
  return { hexIds: [selection.id], workplaceIds: selected.map((f) => f.workplace_id) }
}

export function idFilter(key: string, ids: (string | number)[] | null): FilterSpecification | null {
  if (ids === null) return null
  return ['in', ['get', key], ['literal', ids]]
}

/** Distance in pixels between the centres of dots sharing the same coordinates. */
export const DOT_SPACING = 18

/** A workplace with the horizontal pixel shift and the colour (hex) its dot is drawn with. */
export type PlacedWorkplace = WorkplaceLocation & { dx: number; color: string }

/**
 * Campaigns at the same coordinates get their dots laid out side by side, centred on the
 * true location, instead of drawn over each other. Order is preserved.
 */
export function placeWorkplaces(
  workplaces: WorkplaceLocation[],
  color: (workplace: WorkplaceLocation) => string,
): PlacedWorkplace[] {
  return workplaces.map((wp) => {
    const group = workplaces.filter((other) => other.lat === wp.lat && other.lon === wp.lon)
    const dx = (group.indexOf(wp) - (group.length - 1) / 2) * DOT_SPACING
    return { ...wp, dx, color: color(wp) }
  })
}

/**
 * `icon-offset` expression applying each dot's shift. Array properties of a GeoJSON source
 * reach the style as strings, so every distinct shift is matched to a literal pair instead.
 */
export function iconOffsetExpression(placed: PlacedWorkplace[]): ExpressionSpecification {
  const none: ExpressionSpecification = ['literal', [0, 0]]
  const shifts = [...new Set(placed.map((wp) => wp.dx))].filter((dx) => dx !== 0)
  return shifts.reduce<ExpressionSpecification>(
    (fallback, dx) => ['case', ['==', ['get', 'dx'], dx], ['literal', [dx, 0]], fallback],
    none,
  )
}

/** Where the dot of a workplace is drawn ([lng, lat]) at the map's current view. */
export function dotPosition(m: MaplibreMap, workplace: PlacedWorkplace): [number, number] {
  const point = m.project([workplace.lon, workplace.lat])
  const { lng, lat } = m.unproject([point.x + workplace.dx, point.y])
  return [lng, lat]
}

export interface FlowArc {
  source: [number, number]
  target: [number, number]
  count: number
  /** Colour of the home hexagon on the heatmap, so the arc fades from it to the workplace. */
  sourceColor: RGB
  /** Colour of the workplace dot the arc lands on. */
  targetColor: RGB
}

/** One arc per selected flow, from the home hexagon centroid to the workplace dot ([lng, lat]). */
export function makeFlowArcs(
  selected: HomeWorkplaceFlow[],
  workplacesById: Map<number, PlacedWorkplace>,
  position: (workplace: PlacedWorkplace) => [number, number],
  hexColor: (hexId: string) => RGB,
): FlowArc[] {
  return selected.map((flow) => {
    const workplace = workplacesById.get(flow.workplace_id)
    if (!workplace) throw new Error(`Unknown workplace ${flow.workplace_id} in flows`)
    const [lat, lng] = cellToLatLng(flow.hex_id)
    return {
      source: [lng, lat],
      target: position(workplace),
      count: flow.count,
      sourceColor: hexColor(flow.hex_id),
      targetColor: parseHex(workplace.color),
    }
  })
}
