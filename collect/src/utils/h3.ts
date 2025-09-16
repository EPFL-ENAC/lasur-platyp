import type { Map, MapLayerMouseEvent, LngLatBounds } from 'maplibre-gl'
import * as h3 from 'h3-js'
import type { Feature, FeatureCollection, Polygon } from 'geojson'

// H3 types are available directly from the package
type H3Index = h3.H3Index // This is actually a string
type CoordPair = h3.CoordPair // [lng, lat]

interface H3Feature extends Feature<Polygon> {
  properties: {
    hexId: H3Index
    value?: number
    resolution?: number
    region?: string
  }
}

interface H3FeatureCollection extends FeatureCollection<Polygon> {
  features: H3Feature[]
}

interface Bounds {
  west: number
  south: number
  east: number
  north: number
}

const WORLD_BOUNDS: Bounds = {
  west: -165,
  south: -60,
  east: 170,
  north: 70,
}

const EUROPE_BOUNDS: Bounds = {
  west: -11,
  south: 35,
  east: 40,
  north: 66,
}

const SWISS_BOUNDS: Bounds = {
  west: 5,
  south: 45,
  east: 10,
  north: 49,
}

type H3Selector = (hexId: H3Index) => void

class H3GridManager {
  private map: Map
  private selectionHandler: H3Selector
  private sourceId: string = 'h3-grid'
  private fillLayerId: string = 'h3-grid-fill'
  private outlineLayerId: string = 'h3-grid-outline'

  constructor(map: Map, initSelection: H3Index, selectionHandler: H3Selector) {
    this.map = map
    this.selectionHandler = selectionHandler
    this.initialize(initSelection)
  }

  private initialize(initSelection: H3Index): void {
    if (this.map.loaded()) {
      this.setupGrid(initSelection)
    } else {
      this.map.on('load', () => this.setupGrid(initSelection))
    }
  }

  private isInBounds(bounds: Bounds, lat: number, lng: number): boolean {
    return lng >= bounds.west && lng <= bounds.east && lat >= bounds.south && lat <= bounds.north
  }

  private getWorldHexagons(): H3FeatureCollection {
    return this.getHexagons('world', WORLD_BOUNDS, 20, 2, 1)
  }

  private getEuropeanHexagons(): H3FeatureCollection {
    return this.getHexagons('europe', EUROPE_BOUNDS, 3, 6, 2)
  }

  private getSwissHexagons(): H3FeatureCollection {
    return this.getHexagons('local', SWISS_BOUNDS, 1, 10, 5)
  }

  private getHexagons(
    region: string,
    bounds: Bounds,
    step: number,
    gridNeighbor: number,
    resolution: number,
  ): H3FeatureCollection {
    const features: H3Feature[] = []

    const hexIndices = new Set<string>()

    for (let lat = bounds.south; lat <= bounds.north; lat += step) {
      for (let lng = bounds.west; lng <= bounds.east; lng += step) {
        // Get the hexagon at this center
        const hex = h3.latLngToCell(lat, lng, resolution)
        const ring = h3.gridDisk(hex, gridNeighbor) // Get surrounding hexagons

        ring.forEach((hexIndex) => {
          if (hexIndices.has(hexIndex)) return
          hexIndices.add(hexIndex)
          const boundary = h3.cellToBoundary(hexIndex)
          const centerCoord = h3.cellToLatLng(hexIndex)

          // Skip if this hexagon is in Europe (we'll cover it with higher resolution)
          if (this.isInBounds(bounds, centerCoord[0], centerCoord[1])) {
            features.push({
              type: 'Feature',
              properties: {
                hexId: hexIndex,
                resolution: resolution,
                region: region,
                value: region === 'local' ? 100 : region === 'europe' ? 50 : 0, // Example value
              },
              geometry: {
                type: 'Polygon',
                coordinates: [boundary.map((coord) => [coord[1], coord[0]])], // Convert lat,lng to lng,lat
              },
            })
          }
        })
      }
    }

    return {
      type: 'FeatureCollection',
      features: features,
    }
  }

  private getH3Hexagons(bounds: LngLatBounds, resolution: number): H3Index[] {
    const sw = bounds.getSouthWest()
    const ne = bounds.getNorthEast()

    // Create polygon coordinates in [lng, lat] format for h3-js
    const polygon: CoordPair[] = [
      [sw.lng, sw.lat],
      [ne.lng, sw.lat],
      [ne.lng, ne.lat],
      [sw.lng, ne.lat],
    ]

    // polygonToCells expects the polygon directly
    return h3.polygonToCells(polygon, resolution)
  }

  private setupGrid(initSelection: H3Index): void {
    // Merge sources and layers for different regions
    const worldHexs = this.getWorldHexagons()
    const euroHexs = this.getEuropeanHexagons()
    const localHexs = this.getSwissHexagons()
    const allHexs = {
      type: 'FeatureCollection',
      features: [...worldHexs.features, ...euroHexs.features, ...localHexs.features],
    } as H3FeatureCollection
    this.addSource(allHexs)
    if (initSelection) {
      this.paintHex(initSelection)
      this.showHex(initSelection)
    }
  }

  private addSource(geojson: H3FeatureCollection): void {
    this.map.addSource(this.sourceId, {
      type: 'geojson',
      data: geojson,
    })

    this.map.addLayer({
      id: this.fillLayerId,
      type: 'fill',
      source: this.sourceId,
      layout: {},
      paint: {
        'fill-color': 'rgba(255, 255, 255, 0)', // transparent fill
        'fill-opacity': 0.6,
      },
    })

    this.map.addLayer({
      id: this.outlineLayerId,
      type: 'line',
      source: this.sourceId,
      paint: {
        'line-color': '#016052',
        'line-width': 1,
        // opacity depends on zoom level and on resolution
        'line-opacity': [
          'interpolate',
          ['linear'],
          ['zoom'],
          2,
          ['interpolate', ['linear'], ['get', 'resolution'], 1, 1, 2, 0, 5, 0],
          5,
          ['interpolate', ['linear'], ['get', 'resolution'], 1, 0, 2, 1, 5, 0],
          10,
          ['interpolate', ['linear'], ['get', 'resolution'], 1, 0, 2, 0, 5, 1],
        ],
      },
    })

    this.map.on('mouseenter', this.fillLayerId, () => {
      this.map.getCanvas().style.cursor = 'pointer'
    })

    this.map.on('mouseleave', this.fillLayerId, () => {
      this.map.getCanvas().style.cursor = ''
    })

    this.map.on('click', this.fillLayerId, (e: MapLayerMouseEvent) => {
      //console.log('Zoom level:', this.map.getZoom())
      if (!e.features || e.features.length === 0) return
      // Find feature with the highest resolution
      const highestResFeature = e.features.reduce((prev, curr) => {
        return (prev.properties?.resolution || 0) > (curr.properties?.resolution || 0) ? prev : curr
      })
      if (!highestResFeature || !highestResFeature.properties) return

      // Fill this feature with a different color
      this.paintHex(highestResFeature.properties?.hexId)

      const hexId = highestResFeature.properties.hexId
      if (this.selectionHandler) {
        this.selectionHandler(hexId)
      }
    })
  }

  private paintHex(hexId: H3Index) {
    this.map.setPaintProperty(this.fillLayerId, 'fill-color', [
      'case',
      ['==', ['get', 'hexId'], hexId],
      '#e6a21a',
      'rgba(255, 255, 255, 0)',
    ])
  }

  private showHex(hexId: H3Index): void {
    const [lat, lng] = h3.cellToLatLng(hexId)
    const resolution = h3.getResolution(hexId)
    // update zoom level based on resolution
    const zoom = Math.min(8, 2 + resolution)
    this.map.flyTo({ center: [lng, lat], zoom: zoom, maxDuration: 0 })
  }
}

// Utility functions with proper H3 types
class H3Utils {
  static getHexagonsInRadius(
    center: [number, number], // [lat, lng]
    radiusKm: number,
    resolution: number,
  ): H3Index[] {
    const centerHex = h3.latLngToCell(center[0], center[1], resolution)
    const radius = Math.floor(radiusKm / h3.getHexagonEdgeLengthAvg(resolution, 'km'))
    return h3.gridDisk(centerHex, radius)
  }

  static getCellArea(hexId: H3Index, unit: 'km2' | 'm2' = 'km2'): number {
    return h3.cellArea(hexId, unit)
  }

  static getLatLong(hexId: H3Index): [number, number] {
    return h3.cellToLatLng(hexId)
  }

  static getNeighbors(hexId: H3Index): H3Index[] {
    return h3.gridRing(hexId, 1)
  }

  static areNeighbors(hex1: H3Index, hex2: H3Index): boolean {
    return h3.areNeighborCells(hex1, hex2)
  }

  static getHexagonPath(start: H3Index, end: H3Index): H3Index[] {
    return h3.gridPathCells(start, end)
  }

  static getDistance(hex1: H3Index, hex2: H3Index): number {
    return h3.gridDistance(hex1, hex2)
  }

  static compactCells(hexagons: H3Index[]): H3Index[] {
    return h3.compactCells(hexagons)
  }

  static uncompactCells(hexagons: H3Index[], resolution: number): H3Index[] {
    return h3.uncompactCells(hexagons, resolution)
  }
}
export { H3GridManager, H3Utils, type H3Index }
