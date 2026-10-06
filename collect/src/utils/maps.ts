import { type StyleSpecification, setWorkerUrl } from 'maplibre-gl'
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url'

// maplibre-gl v6 is ESM-only and cannot locate its worker through a bundler:
// route it through Vite's worker pipeline so it ships as a self-contained chunk.
setWorkerUrl(workerUrl)

export const style: StyleSpecification = {
  version: 8,
  sources: {
    osm: {
      type: 'raster',
      tiles: ['https://tile.osm.ch/osm-swiss-style/{z}/{x}/{y}.png'],
      tileSize: 256,
      minzoom: 0,
      maxzoom: 20,
      attribution:
        'data © <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap contributors</a>, map cc-by <a href="https://github.com/xyztobixyz/OSM-Swiss-Style" target="_blank">xyztobixyz</a>, Elevation: ASTER GDEM, EarthEnv-DEM90, CDEM contains information under OGL Canada',
    },
  },
  layers: [
    // {
    //   id: 'classic',
    //   type: 'raster',
    //   source: 'osm',
    // },
    {
      id: 'light',
      type: 'raster',
      source: 'osm',
      paint: {
        'raster-saturation': -0.9,
        'raster-brightness-min': 0.2,
      },
      // layout: { visibility: 'none' },
    },
  ],
}
