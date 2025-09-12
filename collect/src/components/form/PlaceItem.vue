<template>
  <div>
    <div v-if="label" class="text-bold q-mb-md" :class="labelClass || 'text-h4'">{{ label }}</div>
    <div v-if="hint" class="text-h6">{{ hint }}</div>
    <div>
      <div :id="mapId" :style="`--t-height: ${height || '400px'}`" class="mapinput" />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Location } from 'src/models'
import {
  AttributionControl,
  FullscreenControl,
  Map,
  Marker,
  NavigationControl,
  //type IControl,
} from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { style } from 'src/utils/maps'

interface Props {
  modelValue: Location | undefined
  label?: string
  hint?: string
  height?: string
  center?: [number, number]
  zoom?: number
  mapId: string
  labelClass?: string
}
const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const defaultCenter: [number, number] = [6.142873, 46.205066]

const location = ref<Location>({ lon: defaultCenter[0], lat: defaultCenter[1] })
const map = ref<Map>()
let marker: Marker | undefined

onMounted(onInit)

function onInit() {
  location.value = props.modelValue || {}
  const center: [number, number] = props.center
    ? [props.center[0], props.center[1]]
    : props.modelValue
      ? [props.modelValue.lon || defaultCenter[0], props.modelValue.lat || defaultCenter[1]]
      : defaultCenter
  map.value = new Map({
    container: props.mapId,
    center: center,
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
  if (props.modelValue?.lat && props.modelValue?.lon) {
    marker = new Marker().setLngLat([props.modelValue.lon, props.modelValue.lat])
    marker.addTo(map.value)
  }
  map.value.on('click', (e) => {
    location.value.lat = e.lngLat.lat
    location.value.lon = e.lngLat.lng
    onUpdateMarker()
    onUpdate()
  })
}

function onUpdateMarker() {
  if (!map.value) {
    return
  }
  if (marker) {
    marker.remove()
  }
  if (location.value.lat && location.value.lon) {
    marker = new Marker().setLngLat([location.value.lon, location.value.lat])
    marker.addTo(map.value)
    map.value.flyTo({
      center: [location.value.lon, location.value.lat], // New center
      zoom: map.value.getZoom(),
      speed: 2, // Control the animation speed (default: 1.2)
      curve: 1, // Control the smoothness of the curve
      essential: true, // Makes it non-disruptive for screen readers
    })
  }
}

function onUpdate() {
  emit('update:modelValue', location.value)
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
