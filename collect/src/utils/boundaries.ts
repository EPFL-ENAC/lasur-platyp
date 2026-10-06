import {
  type DataDrivenPropertyValueSpecification,
  type Map,
  type MapMouseEvent,
  addProtocol,
} from 'maplibre-gl'
import { Protocol } from 'pmtiles'
import type { BoundaryLevel, PlaceLocation } from '@/models'
import { H3Utils, type H3Index } from '@/utils/h3'

const protocol = new Protocol()
addProtocol('pmtiles', protocol.tile)

const cdnUrl = 'https://enacit4r-cdn.epfl.ch'
const mapsUrl = `${cdnUrl}/platyp/maps/2026-07-06T14:05/data/`

type BoundarySelector = (selection: PlaceLocation | undefined) => void

/**
 * Resolve the location to use for a pro journey: the current `location`
 * field if set, otherwise an approximate one derived from the legacy
 * `hex_id` field for records saved before boundaries replaced the H3 grid.
 */
function resolveLocation(
  location: PlaceLocation | undefined,
  hexId: H3Index | undefined,
): PlaceLocation | undefined {
  if (location) return location
  if (hexId) return H3Utils.toPlaceLocation(hexId)
  return undefined
}

const LEVEL_SOURCES: Record<BoundaryLevel, string> = {
  national: 'national_boundaries',
  regional: 'regional_boundaries',
  local: 'local_boundaries',
}

// From most specific (narrowest coverage, e.g. local is Switzerland-only) to
// most general (national has worldwide coverage). When a click misses at one
// level, e.g. outside the covered area, we fall back to the next one.
const LEVEL_FALLBACK_ORDER: BoundaryLevel[] = ['local', 'regional', 'national']

function getFallbackLevels(level: BoundaryLevel): BoundaryLevel[] {
  return LEVEL_FALLBACK_ORDER.slice(LEVEL_FALLBACK_ORDER.indexOf(level))
}

// Zoom levels at which selection switches from one boundary level to the next
const REGIONAL_MIN_ZOOM = 5
const LOCAL_MIN_ZOOM = 7

// Zoom used to fly to a restored selection, per boundary level
const LEVEL_FLY_ZOOM: Record<BoundaryLevel, number> = {
  national: 3,
  regional: 6,
  local: 8,
}

const HIGHLIGHT_COLOR = '#e6a21a'
const TRANSPARENT = 'rgba(0, 0, 0, 0)'

type BoundariesSourceId = 'national_boundaries' | 'regional_boundaries' | 'local_boundaries'

const BOUNDARIES_SOURCES: Record<
  BoundariesSourceId,
  {
    url: string
    minzoom: number
    maxzoom: number
    opacity: DataDrivenPropertyValueSpecification<number>
  }
> = {
  national_boundaries: {
    url: `${mapsUrl}national_boundaries.pmtiles`,
    minzoom: 0,
    maxzoom: 9,
    opacity: ['interpolate', ['linear'], ['zoom'], 0, 0.4, 7, 0.05],
  },
  regional_boundaries: {
    url: `${mapsUrl}regional_boundaries.pmtiles`,
    minzoom: 0,
    maxzoom: 6,
    opacity: ['interpolate', ['linear'], ['zoom'], 4, 0.05, 5, 0.1, 6, 0.2, 7, 0.4],
  },
  local_boundaries: {
    url: `${mapsUrl}local_boundaries.pmtiles`,
    minzoom: 6,
    maxzoom: 8,
    opacity: ['interpolate', ['linear'], ['zoom'], 6, 0.05, 7, 0.1, 8, 0.2, 9, 0.3, 10, 0.4],
  },
}

class BoundariesManager {
  private map: Map
  private selectionHandler: BoundarySelector | undefined
  private currentSelection: PlaceLocation | undefined

  constructor(
    map: Map,
    initSelection: PlaceLocation | undefined,
    selectionHandler: BoundarySelector | undefined,
  ) {
    this.map = map
    this.selectionHandler = selectionHandler
    this.currentSelection = initSelection
    ;(Object.keys(BOUNDARIES_SOURCES) as BoundariesSourceId[]).forEach((sourceId) =>
      this.addSource(sourceId),
    )

    if (this.selectionHandler) {
      this.map.on('click', (e: MapMouseEvent) => this.onClick(e))
    }

    if (initSelection) {
      if (initSelection.feature_id !== undefined) {
        this.highlightBoundary(initSelection.level, initSelection.feature_id)
      }
      this.map.flyTo({
        center: [initSelection.lon, initSelection.lat],
        zoom: LEVEL_FLY_ZOOM[initSelection.level],
        maxDuration: 0,
        animate: false,
      })
    }
  }

  private isSameBoundary(level: BoundaryLevel, featureId: string | number): boolean {
    return this.currentSelection?.level === level && this.currentSelection?.feature_id === featureId
  }

  private getLevelForZoom(zoom: number): BoundaryLevel {
    if (zoom < REGIONAL_MIN_ZOOM) return 'national'
    if (zoom < LOCAL_MIN_ZOOM) return 'regional'
    return 'local'
  }

  private onClick(e: MapMouseEvent): void {
    const startLevel = this.getLevelForZoom(this.map.getZoom())

    for (const level of getFallbackLevels(startLevel)) {
      const fillLayerId = `${LEVEL_SOURCES[level]}-fill`
      if (!this.map.getLayer(fillLayerId)) continue

      const features = this.map.queryRenderedFeatures(e.point, { layers: [fillLayerId] })
      const feature = features[0]
      if (!feature) continue

      const featureId = feature.properties?.id as string | number | undefined
      if (featureId === undefined || featureId === null) continue

      if (this.isSameBoundary(level, featureId)) {
        this.clearHighlights()
        this.currentSelection = undefined
        this.selectionHandler?.(undefined)
        return
      }

      this.clearHighlights(level)
      this.highlightBoundary(level, featureId)

      this.currentSelection = { lat: e.lngLat.lat, lon: e.lngLat.lng, level, feature_id: featureId }
      this.selectionHandler?.(this.currentSelection)
      return
    }
  }

  private highlightBoundary(level: BoundaryLevel, featureId: string | number): void {
    this.map.setPaintProperty(`${LEVEL_SOURCES[level]}-fill`, 'fill-color', [
      'case',
      ['==', ['get', 'id'], featureId],
      HIGHLIGHT_COLOR,
      TRANSPARENT,
    ])
  }

  private clearHighlights(exceptLevel?: BoundaryLevel): void {
    Object.entries(LEVEL_SOURCES).forEach(([level, sourceId]) => {
      if (level !== exceptLevel) {
        this.map.setPaintProperty(`${sourceId}-fill`, 'fill-color', TRANSPARENT)
      }
    })
  }

  private addSource(sourceId: BoundariesSourceId) {
    if (!this.map.getSource(sourceId)) {
      const source = BOUNDARIES_SOURCES[sourceId]
      // Add pmtiles source for boundaries
      this.map.addSource(sourceId, {
        type: 'vector',
        url: `pmtiles://${BOUNDARIES_SOURCES[sourceId].url}`,
        minzoom: source.minzoom,
        maxzoom: source.maxzoom,
      })

      // Fill layer used for hit-testing on click and for highlighting the selected boundary
      if (!this.map.getLayer(`${sourceId}-fill`)) {
        this.map.addLayer({
          id: `${sourceId}-fill`,
          type: 'fill',
          source: sourceId,
          'source-layer': sourceId,
          paint: {
            'fill-color': TRANSPARENT,
            'fill-opacity': 0.4,
          },
        })

        this.map.on('mouseenter', `${sourceId}-fill`, () => {
          if (this.selectionHandler) this.map.getCanvas().style.cursor = 'pointer'
        })
        this.map.on('mouseleave', `${sourceId}-fill`, () => {
          this.map.getCanvas().style.cursor = ''
        })
      }

      // Add outline layer for boundaries
      if (!this.map.getLayer(`${sourceId}-outline`)) {
        this.map.addLayer({
          id: `${sourceId}-outline`,
          type: 'line',
          source: sourceId,
          'source-layer': sourceId,
          paint: {
            'line-color': '#016052',
            'line-width': 1,
            'line-opacity': source.opacity,
          },
        })
      }
    }
  }
}

export { BoundariesManager, resolveLocation }
