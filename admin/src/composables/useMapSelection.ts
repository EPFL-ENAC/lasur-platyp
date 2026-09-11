import type { Ref } from 'vue'
import { MapboxOverlay } from '@deck.gl/mapbox'
import { ArcLayer } from '@deck.gl/layers'
import {
  Popup,
  type Map as MaplibreMap,
  type MapGeoJSONFeature,
  type MapLayerMouseEvent,
  type MapMouseEvent,
} from 'maplibre-gl'
import type { H3Heatmap, HomeWorkplaceFlow, WorkplaceLocation } from '@/models'
import type { GradientScale, RGB } from '@/utils/colors'
import {
  dotPosition,
  idFilter,
  makeFlowArcs,
  placeWorkplaces,
  sameSelection,
  selectFlows,
  visibleIds,
  type FlowArc,
  type MapSelection,
} from '@/utils/flows'

// Same red as the workplace dots
const WORKPLACE_COLOR: RGB = [239, 68, 68]

interface Options {
  map: Ref<MaplibreMap | undefined>
  workplaces: () => WorkplaceLocation[]
  flows: () => HomeWorkplaceFlow[]
  heatmap: () => H3Heatmap
  gradient: () => GradientScale
  t: (key: string, n?: number) => string
}

/**
 * Clicking a workplace or home hexagon selects it: its flows are drawn and unrelated
 * features hidden until the selection is cleared (same feature, empty map, Escape or reset).
 * Hovering a workplace only shows its tooltip; the selected workplace keeps its tooltip.
 * Layers `heatmap-layer` and `workplace-dots` (symbols using the `workplace-dot` and
 * `workplace-dot-selected` images) must exist on the map. Arcs live on deck.gl's own canvas,
 * which follows every map render (fullscreen included).
 */
export function useMapSelection({ map, workplaces, flows, heatmap, gradient, t }: Options) {
  const popup = new Popup({ closeButton: false, closeOnClick: false, offset: 10 })
  const overlay = new MapboxOverlay({ interleaved: false, layers: [] })
  const selected = ref<MapSelection>(null)
  const workplacesById = computed(
    () => new Map(placeWorkplaces(workplaces()).map((wp) => [wp.id, wp])),
  )
  // Workplace whose tooltip is currently shown, to keep it anchored to the dot
  let tooltipId: number | null = null

  watch(selected, applySelection)

  function reset() {
    selected.value = null
  }

  function addInteractions(m: MaplibreMap) {
    m.addControl(overlay)
    // Hover changes the cursor and shows the workplace tooltip; selection is driven by clicks
    m.on('mouseenter', 'heatmap-layer', () => setCursor('pointer'))
    m.on('mouseleave', 'heatmap-layer', () => setCursor(''))
    m.on('mousemove', 'workplace-dots', onWorkplaceMove)
    m.on('mouseleave', 'workplace-dots', onWorkplaceLeave)
    m.on('click', onClick)
    m.on('move', followDots)
  }

  /** deck.gl's canvas, to composite the arcs into the exported image. */
  function getArcsCanvas(): HTMLCanvasElement | null {
    return overlay.getCanvas()
  }

  function applySelection() {
    const m = map.value
    if (!m || !m.getLayer('workplace-dots')) return
    const current = selected.value
    const selectedFlows = selectFlows(flows(), current)
    const { hexIds, workplaceIds } = visibleIds(selectedFlows, current)
    const selectedHex = current?.kind === 'hex' ? current.id : ''
    const selectedWorkplace = current?.kind === 'workplace' ? current.id : -1

    m.setFilter('heatmap-layer', idFilter('hexId', hexIds))
    m.setFilter('workplace-dots', idFilter('id', workplaceIds))
    m.setPaintProperty('heatmap-layer', 'fill-opacity', [
      'case',
      ['==', ['get', 'hexId'], selectedHex],
      0.9,
      0.6,
    ])
    m.setLayoutProperty('workplace-dots', 'icon-image', [
      'case',
      ['==', ['get', 'id'], selectedWorkplace],
      'workplace-dot-selected',
      'workplace-dot',
    ])
    drawArcs()
    showTooltip(selectedWorkplaceId())
  }

  function drawArcs() {
    const arcs = makeFlowArcs(selectFlows(flows(), selected.value), position, hexColor)
    overlay.setProps({ layers: [makeArcLayer(arcs)] })
  }

  /** Dots keep a fixed pixel shift, so their map position changes with the view. */
  function followDots() {
    if (tooltipId !== null) popup.setLngLat(position(tooltipId))
    if (selected.value !== null) drawArcs()
  }

  /** Map position of a workplace dot, shifted sideways when campaigns share coordinates. */
  function position(workplaceId: number): [number, number] {
    const m = map.value
    const workplace = workplacesById.value.get(workplaceId)
    if (!m || !workplace) throw new Error(`Unknown workplace ${workplaceId} on the map`)
    return dotPosition(m, workplace)
  }

  function selectedWorkplaceId(): number | null {
    return selected.value?.kind === 'workplace' ? selected.value.id : null
  }

  /** Shows the tooltip of one workplace, or hides it when there is none to show. */
  function showTooltip(workplaceId: number | null) {
    const m = map.value
    if (!m || workplaceId === null) {
      popup.remove()
      tooltipId = null
      return
    }
    const workplace = workplacesById.value.get(workplaceId)
    if (!workplace) throw new Error(`Unknown workplace ${workplaceId} on the map`)
    popup.setLngLat(position(workplaceId)).setDOMContent(buildTooltip(workplace)).addTo(m)
    tooltipId = workplaceId
  }

  /** Heatmap colour of a hexagon; every flow hexagon is a heatmap key by construction. */
  function hexColor(hexId: string): RGB {
    const value = heatmap()[hexId]
    if (value === undefined) throw new Error(`Hexagon ${hexId} has flows but no heatmap value`)
    return gradient().rgbAt(value)
  }

  function makeArcLayer(arcs: FlowArc[]) {
    return new ArcLayer<FlowArc>({
      id: 'flow-arcs',
      data: arcs,
      getSourcePosition: (d) => d.source,
      getTargetPosition: (d) => d.target,
      getSourceColor: (d) => d.sourceColor,
      getTargetColor: WORKPLACE_COLOR,
      getWidth: (d) => Math.min(10, 1.5 * Math.sqrt(d.count)),
      getHeight: 0.6,
      widthUnits: 'pixels',
    })
  }

  function toSelection(feature: MapGeoJSONFeature | undefined): MapSelection {
    if (!feature) return null
    if (feature.layer.id === 'workplace-dots') {
      return { kind: 'workplace', id: feature.properties.id as number }
    }
    return { kind: 'hex', id: feature.properties.hexId as string }
  }

  function setCursor(cursor: string) {
    if (map.value) map.value.getCanvas().style.cursor = cursor
  }

  function onWorkplaceMove(e: MapLayerMouseEvent) {
    const next = toSelection(e.features?.[0])
    if (next?.kind !== 'workplace') return
    setCursor('pointer')
    showTooltip(next.id)
  }

  /** Back to the selected workplace's tooltip, if any, once the mouse leaves a dot. */
  function onWorkplaceLeave() {
    setCursor('')
    showTooltip(selectedWorkplaceId())
  }

  function onClick(e: MapMouseEvent) {
    const m = map.value
    if (!m) return
    // Layers are listed top-most first: a dot wins over the hexagon beneath it
    const feature = m.queryRenderedFeatures(e.point, {
      layers: ['workplace-dots', 'heatmap-layer'],
    })[0]
    const next = toSelection(feature)
    selected.value = sameSelection(next, selected.value) ? null : next
  }

  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') selected.value = null
  }

  function buildTooltip(workplace: WorkplaceLocation): HTMLElement {
    // Names are user input: build DOM with textContent, never HTML strings
    const root = document.createElement('div')
    root.className = 'map-tooltip'
    const title = document.createElement('div')
    title.className = 'map-tooltip-title'
    title.textContent =
      workplace.name ?? workplace.address ?? t('stats.locations_heatmap.unnamed_workplace')
    root.appendChild(title)
    const campaign = document.createElement('div')
    campaign.textContent = `${workplace.campaign.name} — ${workplace.campaign.company_name}`
    root.appendChild(campaign)
    const count = document.createElement('div')
    count.className = 'map-tooltip-count'
    count.textContent = t('stats.locations_heatmap.participants', workplace.count)
    root.appendChild(count)
    return root
  }

  return {
    selected,
    addInteractions,
    onKeydown,
    reset,
    getArcsCanvas,
    closePopup: () => popup.remove(),
  }
}
