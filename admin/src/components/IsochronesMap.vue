<template>
  <div>
    <div v-if="label" class="text-bold q-mb-md" :class="labelClass || 'text-h6'">{{ label }}</div>
    <div v-if="hint" class="text-help q-mb-md">{{ hint }}</div>
    <div v-if="modeOptions.length > 1" class="row q-mb-md">
      <q-select
        label="Mode"
        v-model="selectedMode"
        :loading="loadingIsochrones"
        :disable="loadingIsochrones"
        :options="modeOptions"
        option-value="value"
        option-label="label"
        filled
        emit-value
        map-options
        hide-dropdown-icon
        style="min-width: 300px"
        @update:model-value="loadIsochronesData"
      />
      <div v-if="allCategories.size > 0" class="q-mt-md on-right">
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
    <div class="bg-white">
      <div :id="mapId" :style="`--t-height: ${height || '400px'}`" class="mapinput" />
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
import type { IsochronesModes } from 'src/models'

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
const availableModes = ref<IsochronesModes>({})
const loadingIsochrones = ref(false)

const selectedMode = ref<string>('')
const modeOptions = computed(() => {
  return Object.entries(availableModes.value).map(([key, value]) => ({
    label: `${key.toLowerCase()} [${value.join(', ')}]`,
    value: key,
  }))
})

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
  loadIsochronesModes().then(() => {
    loadIsochronesData()
  })
}

async function loadIsochronesModes() {
  const modes = await isoService.getModes()
  availableModes.value = modes || {}
  selectedMode.value =
    props.reco in availableModes.value ? props.reco : Object.keys(modes || {})[0] || 'WALK'
}

async function loadIsochronesData() {
  loadingIsochrones.value = true
  const lon = props.center[0]
  const lat = props.center[1]
  let cutoffSec = [300, 600, 900, 1200, 1800]
  switch (selectedMode.value) {
    case 'WALK':
    case 'BIKE':
      cutoffSec = [600, 1200, 1800, 2400, 3600]
      break
    case 'CAR':
    case 'BUS':
      cutoffSec = [900, 1800, 2700, 3600]
      break
    default:
      cutoffSec = [300, 600, 900, 1200, 1800]
      break
  }
  return isoService
    .computeIsochrones({
      lon,
      lat,
      mode: selectedMode.value,
      cutoffSec,
      datetime: '2025-01-15T06:00:00Z',
      categories: [],
    })
    .then((data) => {
      console.log('Isochrones data:', data)
      if (data?.isochrones) {
        showIsochrones(data?.isochrones)
      }
      if (data?.pois) {
        showPois(data?.pois)
      } else if (data?.isochrones.bbox) {
        // load POIs in the current map bbox
        loadPois(data?.isochrones.bbox as [number, number, number, number])
      }
    })
    .catch((err) => {
      console.error('Error computing isochrones', err)
    })
    .finally(() => {
      loadingIsochrones.value = false
    })
}

async function loadPois(bbox: [number, number, number, number]) {
  if (!map.value) return
  loadingIsochrones.value = true
  const data = await isoService.getPois({
    categories: ['food', 'education', 'service', 'health', 'leisure', 'transport', 'commerce'],
    bbox,
  })
  if (data) {
    showPois(data)
  }
  loadingIsochrones.value = false
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
  allCategories.value.clear()
  // set a color property based on category
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
  if (map.value.getSource('pois')) {
    ;(map.value.getSource('pois') as GeoJSONSource).setData(geojson)
  } else {
    map.value.addSource('pois', {
      type: 'geojson',
      data: geojson,
    })
    map.value.addLayer({
      id: 'pois-layer',
      type: 'circle',
      source: 'pois',
      paint: {
        // zoom level 5 -> 2px, level 15 -> 10px
        'circle-radius': ['interpolate', ['linear'], ['zoom'], 5, 1, 18, 5],
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
