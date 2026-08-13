<template>
  <div>
    <div class="text-h4 text-bold q-mb-md">{{ label }}</div>
    <div v-if="hint" class="text-h6">{{ hint }}</div>

    <AddressInput v-model="addressLocation" :readonly="props.readonly" />

    <div>
      <div :id="mapId" :style="`--t-height: ${height || '400px'}`" class="mapinput" />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AddressLocation } from 'src/models'
import { AttributionControl, FullscreenControl, Map, Marker, NavigationControl } from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { style } from 'src/utils/maps'
import AddressInput from './AddressInput.vue'

interface Props {
  label?: string
  hint?: string
  height?: string
  center?: [number, number]
  zoom?: number
  mapId: string
  readonly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  readonly: false,
})

const addressLocation = defineModel<AddressLocation | undefined>({
  default: () => ({ address: '' }),
})

const map = ref<Map>()
let marker: Marker | undefined

const defaultCenter: [number, number] = [6.142873, 46.205066]

onMounted(() => {
  initMap()
})

onBeforeUnmount(() => {
  marker?.remove()
  map.value?.remove()
})

function initMap() {
  const currentValue = addressLocation.value

  const center: [number, number] = props.center
    ? [props.center[0], props.center[1]]
    : currentValue
      ? [currentValue.lon || defaultCenter[0], currentValue.lat || defaultCenter[1]]
      : defaultCenter

  map.value = new Map({
    container: props.mapId,
    center,
    style,
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

  if (currentValue?.lat != null && currentValue?.lon != null) {
    marker = new Marker().setLngLat([currentValue.lon, currentValue.lat])
    marker.addTo(map.value)
  }

  if (!props.readonly) {
    map.value.on('click', (e) => {
      addressLocation.value = {
        ...(addressLocation.value || { address: '' }),
        lat: e.lngLat.lat,
        lon: e.lngLat.lng,
        address: undefined,
      }

      onUpdateMarker()
    })
  }
}

function onUpdateMarker(flyTo = true) {
  if (!map.value) {
    return
  }

  if (marker) {
    marker.remove()
    marker = undefined
  }

  if (addressLocation.value?.lat != null && addressLocation.value?.lon != null) {
    marker = new Marker().setLngLat([addressLocation.value.lon, addressLocation.value.lat])
    marker.addTo(map.value)

    if (flyTo) {
      map.value.flyTo({
        center: [addressLocation.value.lon, addressLocation.value.lat],
        zoom: map.value.getZoom(),
        speed: 2,
        curve: 1,
        essential: true,
      })
    }
  }
}

watch(
  () => [addressLocation.value?.lat, addressLocation.value?.lon],
  () => {
    onUpdateMarker(true)
  },
)
</script>

<style scoped>
.mapinput {
  height: var(--t-height);
}
</style>
