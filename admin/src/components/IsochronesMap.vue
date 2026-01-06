<template>
  <div>
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
    </div>
    <div class="container">
      <q-btn
        :label="t('record.pois')"
        icon="layers"
        color="white"
        text-color="grey-10"
        no-caps
        class="layers bg-white"
        size="12px"
      >
        <q-menu>
          <q-list>
            <template v-for="pois in poisOptions" :key="pois.value">
              <q-item clickable>
                <q-item-section>{{ pois.label }}</q-item-section>
                <q-item-section side>
                  <q-toggle
                    v-model="showPoisMap[pois.value]"
                    :color="pois.color"
                    keep-color
                    @update:model-value="onShowPoisMap(pois.value)"
                  />
                </q-item-section>
              </q-item>
            </template>
          </q-list>
        </q-menu>
      </q-btn>
      <div :id="mapId" :style="`--t-height: ${height || '400px'}`" class="mapview" />
      <div class="colors q-pa-sm bg-white text-grey-8 text-caption rounded-borders">
        <div class="row q-gutter-sm">
          <div
            v-for="cutoff in selectedModeCutoffSec"
            :key="`color-${cutoff}`"
            class="row items-center"
          >
            <div
              :style="`width: 15px; height: 15px; background-color: ${getCutoffColor(cutoff)}; border: 1px solid #5a3fc0; margin-right: 5px;`"
            ></div>
            <div>{{ t('record.minutes', { count: Math.floor(cutoff / 60) }) }}</div>
          </div>
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
import { style, ISOCHRONE_CUTOFF_COLORS } from 'src/utils/maps'

const isoService = useIsochrones()

interface Props {
  center: [number, number]
  reco: string
  height?: string
  zoom?: number
  mapId: string
  labelClass?: string
}
const props = defineProps<Props>()

const { t } = useI18n()

const map = ref<Map>()
let marker: Marker | undefined
const loadingIsochrones = ref(false)
const isochronesData = ref<GeoJSON.FeatureCollection>()
const selectedMode = ref<string>('WALK')
const selectedModeCutoffSec = ref<number[]>([]) // in seconds
const modeOptions = computed(() => {
  return ['WALK', 'BIKE', 'EBIKE', 'CAR', 'TRANSIT', 'RAIL', 'BUS'].map((m) => {
    return { label: t(`record.mode.${m.toLowerCase()}`), value: m }
  })
})
const poisOptions = computed(() =>
  ['food', 'education', 'service', 'health', 'leisure', 'transport', 'commerce'].map((cat) => ({
    label: t(`record.categories.${cat}`),
    value: cat,
    color: categoryToColor(cat)?.name || 'grey-8',
  })),
)
const showPoisMap = ref<{ [key: string]: boolean }>({
  food: false,
  education: false,
  service: false,
  health: false,
  leisure: false,
  transport: false,
  commerce: false,
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
  loadIsochronesData()
}

async function loadIsochronesData() {
  loadingIsochrones.value = true
  const lon = props.center[0]
  const lat = props.center[1]
  let cutoffSec = []
  let mode = 'WALK'
  let bikeSpeed = 13
  switch (selectedMode.value) {
    case 'WALK':
      mode = 'WALK'
      cutoffSec = [600, 1200, 1800, 2400, 3600]
      break
    case 'BIKE':
      mode = 'BICYCLE'
      cutoffSec = [600, 1200, 1800, 2400, 3600]
      break
    case 'EBIKE':
      mode = 'BICYCLE'
      bikeSpeed = 17
      cutoffSec = [600, 1200, 1800, 2400, 3600]
      break
    case 'CAR':
      mode = 'CAR'
      cutoffSec = [1200, 2400]
      break
    case 'TRANSIT':
      mode = 'TRANSIT'
      cutoffSec = [1200, 2400, 3600]
      break
    case 'RAIL':
      mode = 'RAIL'
      cutoffSec = [1200, 2400, 3600]
      break
    case 'BUS':
      mode = 'BUS'
      cutoffSec = [1200, 2400, 3600]
      break
    default:
      cutoffSec = [300, 600, 900, 1200, 1800]
      break
  }
  selectedModeCutoffSec.value = cutoffSec
  return isoService
    .computeIsochrones({
      lon,
      lat,
      mode,
      bikeSpeed,
      cutoffSec,
      datetime: '2025-01-15T08:30:00Z', // UTC
      categories: [],
    })
    .then((data) => {
      if (data?.isochrones) {
        isochronesData.value = data?.isochrones
        showIsochrones(isochronesData.value)
        if (data?.isochrones.bbox) {
          // load POIs in the current map bbox
          const selected = Object.entries(showPoisMap.value)
            .filter(([, v]) => v)
            .map(([k]) => k)
          if (selected.length > 0) {
            loadPois(selected)
          }
        }
      }
    })
    .catch((err) => {
      console.error('Error computing isochrones', err)
    })
    .finally(() => {
      loadingIsochrones.value = false
    })
}

async function loadPois(categories: string[]) {
  if (!map.value) return
  if (!isochronesData.value || !isochronesData.value.bbox) return
  const bbox = isochronesData.value.bbox as [number, number, number, number]
  loadingIsochrones.value = true
  const data = await isoService.getPois({
    categories,
    bbox,
  })
  if (data) {
    showPois(categories, data)
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
        // fill color depends on the time property with default value #5a3fc0
        'fill-color': [
          'interpolate',
          ['linear'],
          ['get', 'time'],
          300,
          getCutoffColor(300),
          600,
          getCutoffColor(600),
          900,
          getCutoffColor(900),
          1200,
          getCutoffColor(1200),
          1800,
          getCutoffColor(1800),
          2400,
          getCutoffColor(2400),
          3600,
          getCutoffColor(3600),
        ],
        'fill-opacity': 0.3,
        'fill-outline-color': '#5a3fc0',
      },
    })
  }
  // remove pois layers if any
  poisOptions.value.forEach((cat) => {
    const layerId = `pois-layer-${cat.value}`
    if (map.value?.getLayer(layerId)) {
      map.value.removeLayer(layerId)
      map.value.removeSource(layerId)
    }
  })
}

function showPois(categories: string[], geojson: GeoJSON.FeatureCollection) {
  if (!map.value) return
  const sources: { [key: string]: GeoJSON.FeatureCollection } = {}
  // set a color property based on category
  geojson.features.forEach((feature) => {
    if (feature.properties && feature.properties.variable && feature.properties.value) {
      const cat = isoService.findCategory(
        feature.properties.variable as string,
        feature.properties.value as string,
      )
      feature.properties.category = cat
      feature.properties.color = categoryToColor(cat)?.hex || '#000000'
    } else if (feature.properties) {
      feature.properties.color = '#000000'
    }
  })
  // split by category
  geojson.features.forEach((feature) => {
    if (feature.properties && feature.properties.category) {
      const cat = feature.properties.category as string
      if (!(cat in sources)) {
        sources[cat] = { type: 'FeatureCollection', features: [] }
      }
      if (sources[cat]) {
        sources[cat].features.push(feature)
      }
    }
  })
  // add a layer per category
  Object.entries(sources).forEach(([cat, data]) => {
    if (!categories.includes(cat)) return
    const layerId = `pois-layer-${cat}`
    if (map.value?.getSource(layerId)) {
      ;(map.value?.getSource(layerId) as GeoJSONSource).setData(data)
    } else {
      map.value?.addSource(layerId, {
        type: 'geojson',
        data,
      })
      map.value?.addLayer({
        id: layerId,
        type: 'circle',
        source: layerId,
        paint: {
          // zoom level 5 -> 2px, level 15 -> 10px
          'circle-radius': ['interpolate', ['linear'], ['zoom'], 5, 1, 18, 5],
          'circle-color': ['get', 'color'],
        },
      })
      // hide if not selected
      if (map.value?.getLayer(layerId) && !showPoisMap.value[cat]) {
        map.value.setLayoutProperty(layerId, 'visibility', 'none')
      }
    }
  })
}

function onShowPoisMap(name: string) {
  if (!map.value) return
  const layerId = `pois-layer-${name}`
  const hasLayer = map.value.getLayer(layerId) !== undefined
  if (!hasLayer) {
    // load POIs in the current map bbox
    if (map.value) {
      const bbox = isochronesData.value?.bbox as [number, number, number, number]
      if (!bbox) return
      loadPois([name])
    }
    return
  }
  // show/hide layer
  if (showPoisMap.value[name]) {
    if (map.value.getLayer(layerId)) {
      map.value.setLayoutProperty(layerId, 'visibility', 'visible')
    }
  } else {
    if (map.value.getLayer(layerId)) {
      map.value.setLayoutProperty(layerId, 'visibility', 'none')
    }
  }
}

function categoryToColor(str: string): { name: string; hex: string } | undefined {
  const mapColors: { [key: string]: { name: string; hex: string } } = {
    food: { name: 'red-9', hex: '#c62828' },
    education: { name: 'purple-9', hex: '#6a1b9a' },
    service: { name: 'blue-8', hex: '#1976d2' },
    health: { name: 'green-13', hex: '#00e676' },
    leisure: { name: 'light-green-9', hex: '#558b2f' },
    transport: { name: 'yellow-8', hex: '#fbc02d' },
    commerce: { name: 'pink-4', hex: '#f06292' },
  }
  if (str in mapColors && mapColors[str]) {
    return mapColors[str]
  }
}

function getCutoffColor(cutoff: number): string {
  return ISOCHRONE_CUTOFF_COLORS[cutoff] || '#5a3fc0'
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
  opacity: 0; /* Start or end with opacity 0 for the fade effect */
}

.container {
  position: relative; /* Needed for absolute children */
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
