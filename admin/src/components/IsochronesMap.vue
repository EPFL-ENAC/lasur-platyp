<template>
  <div>
    <div v-if="label" class="text-bold q-mb-md" :class="labelClass || 'text-h6'">{{ label }}</div>
    <div v-if="hint" class="text-help q-mb-md">{{ hint }}</div>
    <div class="bg-white">
      <div :id="mapId" :style="`--t-height: ${height || '400px'}`" class="mapinput" />
    </div>
    <div v-if="allCategories.size > 0" class="q-mt-md">
      <div class="text-subtitle1 q-mb-sm">Categories</div>
      <div class="q-gutter-sm row">
        <div v-for="cat in Array.from(allCategories).sort()" :key="cat" class="row items-center">
          <div
            :style="`width: 16px; height: 16px; background-color: ${stringToHexColor(cat)}; border: 1px solid #000; margin-right: 4px;`"
          ></div>
          <div>{{ cat }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  AttributionControl,
  FullscreenControl,
  Map,
  Marker,
  NavigationControl,
  type GeoJSONSource,
} from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { style } from 'src/utils/maps'

const isoService = useIsochrones()

interface Props {
  center: [number, number]
  reco: string
  label?: string
  hint?: string
  height?: string
  zoom?: number
  mapId: string
  labelClass?: string
}
const props = defineProps<Props>()

const map = ref<Map>()
let marker: Marker | undefined
const allCategories = ref(new Set<string>())

onMounted(onInit)

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
  marker = new Marker().setLngLat([props.center[0], props.center[1]])
  marker.addTo(map.value)
  loadIsochrones()
}

function loadIsochrones() {
  if (!map.value) return
  const lon = props.center[0]
  const lat = props.center[1]
  const cutoffSec = [1800, 3600, 5400]
  isoService
    .computeIsochrones({
      lon,
      lat,
      cutoffSec,
      datetime: new Date().toISOString(),
      categories: ['food', 'education', 'service', 'health', 'leisure', 'transport', 'commerce'],
    })
    .then((data) => {
      console.log('Isochrones data:', data)
      if (data?.isochrones) {
        showIsochrones(data?.isochrones)
      }
      if (data?.pois) {
        showPois(data?.pois)
      }
    })
    .catch((err) => {
      console.error('Error computing isochrones', err)
    })
}

function showIsochrones(geojson: GeoJSON.FeatureCollection) {
  if (!map.value) return
  if (map.value.getSource('isochrones')) {
    ;(map.value.getSource('isochrones') as GeoJSONSource).setData(geojson)
  } else {
    map.value.addSource('isochrones', {
      type: 'geojson',
      data: geojson,
    })
    map.value.addLayer({
      id: 'isochrones-layer',
      type: 'fill',
      source: 'isochrones',
      paint: {
        'fill-color': '#5a3fc0',
        'fill-opacity': 0.3,
        'fill-outline-color': '#5a3fc0',
      },
    })
  }
}

function showPois(geojson: GeoJSON.FeatureCollection) {
  if (!map.value) return
  if (map.value.getSource('pois')) {
    ;(map.value.getSource('pois') as GeoJSONSource).setData(geojson)
  } else {
    // set a color property based on category
    allCategories.value.clear()
    geojson.features.forEach((feature) => {
      if (feature.properties && feature.properties.variable && feature.properties.value) {
        const cat = isoService.findCategory(
          feature.properties.variable as string,
          feature.properties.value as string,
        )
        feature.properties.category = cat
        feature.properties.color = stringToHexColor(cat)
        allCategories.value.add(cat)
      } else if (feature.properties) {
        feature.properties.color = '#000000'
      }
    })
    map.value.addSource('pois', {
      type: 'geojson',
      data: geojson,
    })
    map.value.addLayer({
      id: 'pois-layer',
      type: 'circle',
      source: 'pois',
      paint: {
        'circle-radius': 6,
        'circle-color': ['get', 'color'],
      },
    })
  }
}

function stringToHexColor(str: string): string {
  // simple non-cryptographic hash
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i)
    // convert to 32bit int
    hash |= 0
  }

  // build color from hash
  const r = (hash >> 16) & 0xff
  const g = (hash >> 8) & 0xff
  const b = hash & 0xff

  return '#' + [r, g, b].map((n) => n.toString(16).padStart(2, '0')).join('')
}
</script>

<style scoped>
.mapinput {
  height: var(--t-height);
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0; /* Start or end with opacity 0 for the fade effect */
}
</style>
