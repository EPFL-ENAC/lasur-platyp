<template>
  <div>
    <div v-if="label" class="question-label text-bold q-mb-md">{{ label }}</div>
    <div v-if="hint" class="question-hint q-mb-lg">{{ hint }}</div>

    <AddressInput v-model="addressLocation" :readonly="props.readonly" />

    <div :id="mapId" :style="`--t-height: ${height || '400px'}`" class="mapinput q-mt-md" />
  </div>
</template>

<script setup lang="ts">
import type { AddressLocation } from '@/models'
import {
  AttributionControl,
  FullscreenControl,
  type LngLat,
  Map,
  Marker,
  NavigationControl,
} from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import type { Point } from 'geojson'
import { style } from '@/utils/maps'
import { geocoderApi, toAddress } from '@/utils/geocoder'
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
    }),
  )

  if (currentValue?.lat != null && currentValue?.lon != null) {
    marker = new Marker().setLngLat([currentValue.lon, currentValue.lat])
    marker.addTo(map.value)
  }

  // readonly can change after mount (e.g. "other" workplace selected)
  map.value.on('click', (e) => {
    if (!props.readonly) void onMapClick(e.lngLat)
  })
}

// Snap to the nearest address, so the point does not land in a lake or a field
async function onMapClick(lngLat: LngLat) {
  const { features } = await geocoderApi.reverseGeocode({
    query: { lat: lngLat.lat, lon: lngLat.lng },
  })
  const snapped = features[0]
  const [lon, lat] = snapped ? (snapped.geometry as Point).coordinates : [lngLat.lng, lngLat.lat]
  addressLocation.value = {
    ...(addressLocation.value || { address: '' }),
    lat,
    lon,
    address: snapped ? toAddress(snapped) : undefined,
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

<style scoped lang="scss">
// The map is content like any other field: same border and corner as the rest.
.mapinput {
  height: var(--t-height);
  border: 1px solid var(--secondary-border-color);
  border-radius: $button-border-radius;
  overflow: hidden;
}
</style>
