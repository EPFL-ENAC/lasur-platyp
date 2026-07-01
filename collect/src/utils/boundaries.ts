import { type Map, addProtocol } from 'maplibre-gl'
import { Protocol } from 'pmtiles'

const protocol = new Protocol()
addProtocol('pmtiles', protocol.tile)

const cdnUrl = 'https://enacit4r-cdn.epfl.ch'
const mapsUrl = `${cdnUrl}/platyp/maps/2026-07-01T10:21/data/`

const BOUNDARIES_SOURCES = {
  national_boundaries: {
    url: `${mapsUrl}national_boundaries.pmtiles`,
    minzoom: 0,
    maxzoom: 7,
    opacity: ['interpolate', ['linear'], ['zoom'], 0, 0.4, 7, 0],
  },
  filtering_boundaries: {
    url: `${mapsUrl}filtering_boundaries.pmtiles`,
    minzoom: 6,
    maxzoom: 10,
    opacity: ['interpolate', ['linear'], ['zoom'], 6, 0.2, 7, 0.4, 9, 0.2, 10, 0],
  },
  regional_boundaries: {
    url: `${mapsUrl}regional_boundaries.pmtiles`,
    minzoom: 6,
    maxzoom: 10,
    opacity: ['interpolate', ['linear'], ['zoom'], 6, 0.2, 7, 0.4, 9, 0.2, 10, 0],
  },
  local_boundaries: {
    url: `${mapsUrl}local_boundaries.pmtiles`,
    minzoom: 0,
    maxzoom: 22,
    opacity: 0.4, //['interpolate', ['linear'], ['zoom'], 10, 0.4, 14, 0.4, 22, 0.4],
  },
}

class BoundariesManager {
  private map: Map
  private sourceId: string = 'boundaries'
  private fillLayerId: string = 'boundaries-fill'
  private outlineLayerId: string = 'boundaries-outline'

  constructor(map: Map) {
    this.map = map
    Object.keys(BOUNDARIES_SOURCES).forEach((sourceId) => this.addSource(sourceId))
  }

  private addSource(sourceId: string) {
    if (!this.map.getSource(sourceId)) {
      const source = BOUNDARIES_SOURCES[sourceId]
      // Add pmtiles source for boundaries
      this.map.addSource(sourceId, {
        type: 'vector',
        url: `pmtiles://${BOUNDARIES_SOURCES[sourceId].url}`,
        minzoom: source.minzoom,
        maxzoom: source.maxzoom,
      })

      // Add fill layer for boundaries
      if (!this.map.getLayer(`${sourceId}-fill`)) {
        this.map.addLayer({
          id: `${sourceId}-fill`,
          type: 'fill',
          source: sourceId,
          'source-layer': sourceId,
          paint: {
            'fill-color': '#888888',
            'fill-opacity': source.opacity,
          },
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
            'line-color': '#000000',
            'line-width': 1,
            'line-opacity': source.opacity,
          },
        })
      }
    }
  }
}

export { BoundariesManager }
