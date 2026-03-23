<template>
  <div class="map-container" :style="`--t-height: ${height || '400px'}`">
    <div :id="mapId" class="mapview"></div>

    <!-- Legend Overlay -->
    <div class="map-legend">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  AttributionControl,
  FullscreenControl,
  LngLatBounds,
  Map,
  NavigationControl,
  type GeoJSONSource,
} from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { style } from 'src/utils/maps'
import { cellToBoundary } from 'h3-js'
import type { GradientScale } from 'src/utils/colors'
import { H3Heatmap } from 'src/models'

interface Dot {
  lat: number
  lon: number
}

interface HeatmapGeoJSON {
  shape: GeoJSON.FeatureCollection<GeoJSON.Polygon, { value: number }>
  workplaces: GeoJSON.FeatureCollection<GeoJSON.Point> | null
  boundingBox: LngLatBounds
}

interface Props {
  h3Heatmap: H3Heatmap
  dots?: Dot[]
  heatmapGradient: GradientScale
  center: [number, number]
  height?: string
  zoom?: number
  mapId: string
}
const props = defineProps<Props>()

const map = ref<Map>()

onMounted(onInit)
onUnmounted(() => {
  if (map.value) {
    map.value.remove()
    map.value = undefined
  }
})

watch([() => props.h3Heatmap, () => props.dots], () => {
  if (map.value) {
    const source = map.value.getSource('heatmap-data') as GeoJSONSource
    const workplaceSource = map.value.getSource('workplace-data') as GeoJSONSource
    if (source) {
      const geoJson = makeGeoJSON()
      source.setData(geoJson.shape)
      if (workplaceSource) {
        workplaceSource.setData(
          geoJson.workplaces ?? {
            type: 'FeatureCollection',
            features: [],
          },
        )
      }
      map.value.fitBounds(geoJson.boundingBox, { padding: 20, duration: 500 })
    }
  }
})

function makeGeoJSON(): HeatmapGeoJSON {
  const boundingBox = new LngLatBounds()
  const shape: GeoJSON.FeatureCollection<GeoJSON.Polygon, { value: number }> = {
    type: 'FeatureCollection',
    features: Object.entries(props.h3Heatmap).map(([hexId, value]) => {
      const boundary = cellToBoundary(hexId, true)
      boundary.forEach((coord) => boundingBox.extend(coord))

      return {
        type: 'Feature',
        geometry: {
          type: 'Polygon',
          coordinates: [boundary],
        },
        properties: {
          value,
        },
      }
    }),
  }

  const workplaceFeatures: GeoJSON.Feature<GeoJSON.Point>[] = (props.dots || []).map((wp) => {
    boundingBox.extend([wp.lon, wp.lat])
    return {
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: [wp.lon, wp.lat],
      },
      properties: {},
    }
  })

  return {
    shape,
    workplaces: {
      type: 'FeatureCollection',
      features: workplaceFeatures,
    },
    boundingBox,
  }
}

function onInit() {
  map.value = new Map({
    container: props.mapId,
    center: props.center,
    style: style,
    trackResize: true,
    zoom: props.zoom || 14,
    attributionControl: false,
  })
  map.value.addControl(new NavigationControl({}))
  map.value.addControl(new FullscreenControl({}))
  map.value.addControl(
    new AttributionControl({
      compact: true,
      customAttribution:
        '© <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>',
    }),
  )

  map.value.on('load', () => {
    if (!map.value) return

    const geoJson = makeGeoJSON()
    map.value.addSource('heatmap-data', {
      type: 'geojson',
      data: geoJson.shape,
    })
    map.value.addLayer({
      id: 'heatmap-layer',
      type: 'fill',
      source: 'heatmap-data',
      paint: {
        // Color the hexagons based on the 'value' property
        'fill-color': props.heatmapGradient.toMapLibreExpression('value'),
        'fill-opacity': 0.6,
        'fill-outline-color': '#ffffff',
      },
    })

    map.value.addSource('workplace-data', {
      type: 'geojson',
      data: geoJson.workplaces ?? {
        type: 'FeatureCollection',
        features: [],
      },
    })

    console.log(geoJson)

    // 3. Workplace Circle Layer (The dot)
    map.value.addLayer({
      id: 'workplace-dots',
      type: 'circle',
      source: 'workplace-data',
      paint: {
        'circle-radius': 5,
        'circle-color': '#EF4444',
        'circle-stroke-width': 2,
        'circle-stroke-color': '#FFFFFF',
      },
    })

    map.value.fitBounds(geoJson.boundingBox, { padding: 20, duration: 500 })
  })
}
</script>

<style scoped>
.map-container {
  position: relative;
  width: 100%;
  height: var(--t-height);
}

.mapview {
  width: 100%;
  height: 100%;
}

.map-legend {
  position: absolute;
  bottom: 0.5rem;
  left: 0.5rem;
  z-index: 2;
  background: white;
  padding: 12px;
  border-radius: 4px;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
  font-family: sans-serif;
  font-size: 12px;
  color: #333;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 150px;
}
</style>
