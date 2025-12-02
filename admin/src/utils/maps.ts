import { type StyleSpecification } from 'maplibre-gl'

export const style: StyleSpecification = {
  version: 8,
  sources: {
    osm: {
      type: 'raster',
      tiles: ['https://tile.osm.ch/osm-swiss-style/{z}/{x}/{y}.png'],
      tileSize: 256,
      minzoom: 0,
      maxzoom: 20,
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

export const ISOCHRONE_CUTOFF_COLORS: { [key: number]: string } = {
  // dark green
  300: '#1b5e20',
  // lighter green
  600: '#4caf50',
  // lightest green
  900: '#a5d6a7',
  // yellow
  1200: '#ffeb3b',
  // orange
  1800: '#ff9800',
  // red
  2400: '#f44336',
  // dark red
  3600: '#b71c1c',
}
