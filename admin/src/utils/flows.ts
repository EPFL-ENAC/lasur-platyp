import { cellToLatLng } from 'h3-js'
import type { FilterSpecification } from 'maplibre-gl'
import type { HomeWorkplaceFlow, WorkplaceLocation } from '@/models'
import type { RGB } from '@/utils/colors'

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

export interface FlowArc {
  source: [number, number]
  target: [number, number]
  count: number
  /** Colour of the home hexagon on the heatmap, so the arc fades from it to the workplace. */
  sourceColor: RGB
}

/** One arc per selected flow, from the home hexagon centroid to the workplace ([lng, lat]). */
export function makeFlowArcs(
  selected: HomeWorkplaceFlow[],
  workplacesById: Map<number, WorkplaceLocation>,
  hexColor: (hexId: string) => RGB,
): FlowArc[] {
  return selected.map((flow) => {
    const workplace = workplacesById.get(flow.workplace_id)
    if (!workplace) throw new Error(`Unknown workplace ${flow.workplace_id} in flows`)
    const [lat, lng] = cellToLatLng(flow.hex_id)
    return {
      source: [lng, lat],
      target: [workplace.lon, workplace.lat],
      count: flow.count,
      sourceColor: hexColor(flow.hex_id),
    }
  })
}
