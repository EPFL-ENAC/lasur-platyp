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
  idFilter,
  makeFlowArcs,
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
 * Hovering a workplace or home hexagon previews its flows and hides unrelated features;
 * clicking pins that preview so it survives mouse movement. Layers `heatmap-layer` and
 * `workplace-dots` must exist on the map. Arcs live on deck.gl's own canvas, which
 * follows every map render (fullscreen included).
 */
export function useMapSelection({ map, workplaces, flows, heatmap, gradient, t }: Options) {
  const popup = new Popup({ closeButton: false, closeOnClick: false, offset: 10 })
  const overlay = new MapboxOverlay({ interleaved: false, layers: [] })
  const pinned = ref<MapSelection>(null)
  const hovered = ref<MapSelection>(null)
  const active = computed<MapSelection>(() => hovered.value ?? pinned.value)
  const workplacesById = computed(() => new Map(workplaces().map((wp) => [wp.id, wp])))

  watch(active, applySelection)

  function reset() {
    hovered.value = null
    pinned.value = null
  }

  function addInteractions(m: MaplibreMap) {
    m.addControl(overlay)
    m.on('mousemove', 'workplace-dots', onWorkplaceMove)
    m.on('mouseleave', 'workplace-dots', onLeave)
    m.on('mousemove', 'heatmap-layer', onHexMove)
    m.on('mouseleave', 'heatmap-layer', onLeave)
    m.on('click', onClick)
  }

  /** deck.gl's canvas, to composite the arcs into the exported image. */
  function getArcsCanvas(): HTMLCanvasElement | null {
    return overlay.getCanvas()
  }

  function applySelection() {
    const m = map.value
    if (!m || !m.getLayer('workplace-dots')) return
    const current = active.value
    const selected = selectFlows(flows(), current)
    const { hexIds, workplaceIds } = visibleIds(selected, current)
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
    m.setPaintProperty('workplace-dots', 'circle-radius', [
      'case',
      ['==', ['get', 'id'], selectedWorkplace],
      8,
      5,
    ])
    overlay.setProps({
      layers: [makeArcLayer(makeFlowArcs(selected, workplacesById.value, hexColor))],
    })
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
    const m = map.value
    const next = toSelection(e.features?.[0])
    if (!m || next?.kind !== 'workplace') return
    setCursor('pointer')
    if (!sameSelection(next, hovered.value)) hovered.value = next
    const workplace = workplacesById.value.get(next.id)
    if (!workplace) throw new Error(`Unknown workplace ${next.id} on the map`)
    popup.setLngLat([workplace.lon, workplace.lat]).setDOMContent(buildTooltip(workplace)).addTo(m)
  }

  function onHexMove(e: MapLayerMouseEvent) {
    const m = map.value
    if (!m) return
    // Dots are drawn above hexagons: let the dot win when both are under the cursor
    if (m.queryRenderedFeatures(e.point, { layers: ['workplace-dots'] }).length > 0) return
    const next = toSelection(e.features?.[0])
    if (next?.kind !== 'hex') return
    setCursor('pointer')
    if (!sameSelection(next, hovered.value)) hovered.value = next
  }

  function onLeave() {
    setCursor('')
    popup.remove()
    hovered.value = null
  }

  function onClick(e: MapMouseEvent) {
    const m = map.value
    if (!m) return
    const feature = m.queryRenderedFeatures(e.point, {
      layers: ['workplace-dots', 'heatmap-layer'],
    })[0]
    const next = toSelection(feature)
    pinned.value = sameSelection(next, pinned.value) ? null : next
  }

  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') pinned.value = null
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
    workplace.campaigns.forEach((campaign) => {
      const line = document.createElement('div')
      line.textContent = `${campaign.name} — ${campaign.company_name}`
      root.appendChild(line)
    })
    const count = document.createElement('div')
    count.className = 'map-tooltip-count'
    count.textContent = t('stats.locations_heatmap.participants', workplace.count)
    root.appendChild(count)
    return root
  }

  return {
    pinned,
    addInteractions,
    onKeydown,
    reset,
    getArcsCanvas,
    closePopup: () => popup.remove(),
  }
}
