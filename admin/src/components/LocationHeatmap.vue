<template>
  <div :id="mapId" :style="`--t-height: ${height || '400px'}`" class="mapview" />
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

type H3HeatmapData = {
  [hexId: string]: number
};

interface HeatmapGeoJSON {
  shape: GeoJSON.FeatureCollection<GeoJSON.Polygon, { value: number }>
  boundingBox: LngLatBounds
}

interface Props {
  data: H3HeatmapData
  center: [number, number]
  height?: string
  zoom?: number
  mapId: string
  labelClass?: string
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

watch(() => props.data, () => {
  if (map.value) {
    const source = map.value.getSource('heatmap-data') as GeoJSONSource
    if (source) {
      const geoJson = makeGeoJSON()
      source.setData(geoJson.shape)
      map.value.fitBounds(geoJson.boundingBox, { padding: 20, duration: 500 })
    }
  }
})

function makeGeoJSON(): HeatmapGeoJSON {
  const boundingBox = new LngLatBounds()
  const shape: GeoJSON.FeatureCollection<GeoJSON.Polygon, { value: number }> = {
    type: 'FeatureCollection',
    features: Object.entries(props.data).map(([hexId, value]) => {
      const boundary = cellToBoundary(hexId, true)
      boundary.forEach(coord => boundingBox.extend(coord))
      
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

  return {
    shape,
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
    });
    map.value.addLayer({
      id: 'heatmap-layer',
      type: 'fill',
      source: 'heatmap-data',
      paint: {
        // Color the hexagons based on the 'value' property
        'fill-color': [
          'interpolate',
          ['linear'],
          ['get', 'value'],
          0, '#440154', // Dark Purple (Low)
          25, '#3b528b', // Blue
          50, '#21918c', // Teal/Green
          75, '#5ec962', // Light Green
          100, '#fde725'  // Yellow (High)
        ],
        'fill-opacity': 0.6,
        'fill-outline-color': '#ffffff'
      }
    });

    map.value.fitBounds(geoJson.boundingBox, { padding: 20, duration: 500 })
  })

}

</script>

<style scoped>
.mapview {
  position: relative;
  z-index: 1;
  width: var(--t-width);
  height: var(--t-height);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  /* Start or end with opacity 0 for the fade effect */
}

.container {
  position: relative;
  /* Needed for absolute children */
}

.layers {
  position: absolute;
  z-index: 10;
  top: 10px;
  left: 10px;
}

.colors {
  position: absolute;
  z-index: 10;
  bottom: 10px;
  left: 10px;
}
</style>
