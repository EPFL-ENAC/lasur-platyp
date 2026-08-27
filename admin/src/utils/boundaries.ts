import { type Map, type MapMouseEvent, addProtocol } from 'maplibre-gl'
import { Protocol } from 'pmtiles'
import type { Position } from 'geojson'
import type { BoundaryLevel, PlaceLocation } from '@/components/models'

const protocol = new Protocol()
addProtocol('pmtiles', protocol.tile)

const cdnUrl = 'https://enacit4r-cdn.epfl.ch'
const mapsUrl = `${cdnUrl}/platyp/maps/2026-07-06T14:05/data/`

type BoundarySelector = (selection: PlaceLocation | undefined) => void

const LEVEL_SOURCES: Record<BoundaryLevel, string> = {
  filtering: 'filtering_boundaries',
}

// From most specific (narrowest coverage, e.g. local is Switzerland-only) to
// most general (national has worldwide coverage). When a click misses at one
// level, e.g. outside the covered area, we fall back to the next one.
const LEVEL_FALLBACK_ORDER: BoundaryLevel[] = ['filtering']

function getFallbackLevels(level: BoundaryLevel): BoundaryLevel[] {
  return LEVEL_FALLBACK_ORDER.slice(LEVEL_FALLBACK_ORDER.indexOf(level))
}

// Zoom levels at which selection switches from one boundary level to the next
const LOCAL_MIN_ZOOM = 7

// Zoom used to fly to a restored selection, per boundary level
const LEVEL_FLY_ZOOM: Record<BoundaryLevel, number> = {
  filtering: 8,
}

const HIGHLIGHT_COLOR = '#e6a21a'
const TRANSPARENT = 'rgba(0, 0, 0, 0)'

// The filtering_boundaries tiles carry no generic "id" property, only the
// source OSM id, which is unique per feature and used as the identifier here.
const FEATURE_ID_PROPERTY = 'osm_id'

const BOUNDARIES_SOURCES = {
  filtering_boundaries: {
    url: `${mapsUrl}filtering_boundaries.pmtiles`,
    minzoom: 0,
    maxzoom: 6,
    opacity: 0.4, //['interpolate', ['linear'], ['zoom'], 4, 0.05, 5, 0.1, 6, 0.2, 7, 0.4],
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
    ;(Object.keys(BOUNDARIES_SOURCES) as (keyof typeof BOUNDARIES_SOURCES)[]).forEach((sourceId) =>
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

  /**
   * Reconstruct the geometry of a selected boundary feature from the vector tiles
   * currently loaded for its source. Each tile fragment is the intersection of the
   * original feature with that tile's extent, so combining every fragment that
   * shares the feature id into a MultiPolygon preserves point-in-polygon semantics
   * even though the tiles are not stitched back into a single topological shape.
   * Fragments outside the tiles loaded so far (e.g. never panned/zoomed into) are
   * missed, so the result may be incomplete for features that span a wide area.
   */
  getBoundaryGeometry(
    level: BoundaryLevel,
    featureId: string | number,
  ): GeoJSON.Polygon | GeoJSON.MultiPolygon | undefined {
    const sourceId = LEVEL_SOURCES[level]
    const features = this.map.querySourceFeatures(sourceId, {
      sourceLayer: sourceId,
      filter: ['==', ['get', FEATURE_ID_PROPERTY], featureId],
    })

    const polygons: Position[][][] = []
    features.forEach((feature) => {
      const geometry = feature.geometry
      if (geometry.type === 'Polygon') {
        polygons.push(geometry.coordinates)
      } else if (geometry.type === 'MultiPolygon') {
        polygons.push(...geometry.coordinates)
      }
    })

    if (polygons.length === 0) return undefined
    if (polygons.length === 1) return { type: 'Polygon', coordinates: polygons[0] as Position[][] }
    return { type: 'MultiPolygon', coordinates: polygons }
  }

  private isSameBoundary(level: BoundaryLevel, featureId: string | number): boolean {
    return this.currentSelection?.level === level && this.currentSelection?.feature_id === featureId
  }

  private getLevelForZoom(zoom: number): BoundaryLevel {
    if (zoom < LOCAL_MIN_ZOOM) return 'filtering'
    return 'filtering'
  }

  private onClick(e: MapMouseEvent): void {
    const startLevel = this.getLevelForZoom(this.map.getZoom())

    for (const level of getFallbackLevels(startLevel)) {
      const fillLayerId = `${LEVEL_SOURCES[level]}-fill`
      if (!this.map.getLayer(fillLayerId)) continue

      const features = this.map.queryRenderedFeatures(e.point, { layers: [fillLayerId] })
      const feature = features[0]
      if (!feature) continue

      const featureId = feature.properties?.[FEATURE_ID_PROPERTY] as string | number | undefined
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
      ['==', ['get', FEATURE_ID_PROPERTY], featureId],
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

  private addSource(sourceId: keyof typeof BOUNDARIES_SOURCES) {
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

export { BoundariesManager }
