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
