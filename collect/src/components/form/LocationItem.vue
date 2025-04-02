<template>
  <div>
    <div class="text-h4 text-bold q-mb-md">{{ label }}</div>
    <div v-if="hint" class="text-h6">{{ hint }}</div>
    <div class="q-mt-lg">
      <div
        class="row q-pt-sm q-pl-md q-pb-sm q-pr-md rounded-borders q-mb-md bg-primary text-green-3"
      >
        <div class="col">
          <span v-if="hasLocation" class="text-h6 text-white">
            <q-icon name="location_on" color="white" class="q-pb-xs" />
            {{ formatCoordinates(addressLocation.lat, addressLocation.lon) }}
          </span>
          <div v-else class="text-subtitle1">
            {{ t('lookup_address_or_select_on_map') }}
          </div>
        </div>
        <div class="col-auto">
          <q-btn
            v-if="hasLocation"
            flat
            rounded
            dense
            size="sm"
            color="white"
            icon="delete"
            @click="onRemoveLocation"
            class="q-mt-xs"
          />
        </div>
      </div>

      <div class="row q-mb-sm">
        <div class="col-auto q-mt-xs">
          <q-btn color="primary" icon="search" @click="showInput = !showInput" />
        </div>
        <div class="col">
          <transition name="fade">
            <q-input
              v-if="showInput"
              v-model="addressLocation.address"
              type="text"
              class="on-right"
              bg-color="green-3"
              filled
              dense
              :placeholder="t('type_enter_to_lookup_address')"
              @keyup.enter="onSuggestAddress"
              @update:model-value="onUpdate"
              :loading="loading"
              lazy-rules
              style="min-width: 250px"
            >
              <q-menu v-model="showSuggestions" no-parent-event no-focus auto-close>
                <q-list style="min-width: 100px">
                  <q-item
                    clickable
                    v-close-popup
                    v-for="sugg in suggestions"
                    :key="sugg.value"
                    @click="onSuggestionSelected(sugg)"
                  >
                    <q-item-section>{{ sugg.value }}</q-item-section>
                  </q-item>
                  <q-item v-if="suggestions.length === 0">
                    <q-item-section class="text-grey">
                      {{ t('no_results') }}
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-menu>
            </q-input>
          </transition>
        </div>
      </div>
    </div>
    <div>
      <div :id="mapId" :style="`--t-height: ${height || '400px'}`" class="mapinput" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { geocoderApi, toAddress } from 'src/utils/geocoder'
import type { Feature, Point } from 'geojson'
import type { AddressLocation } from 'src/models'
import { formatCoordinates } from 'src/utils/numbers'
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

const { t } = useI18n()

interface Props {
  modelValue: AddressLocation | undefined
  label?: string
  hint?: string
  height?: string
  center?: [number, number]
  zoom?: number
  mapId: string
}
const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

interface Suggestion {
  value: string
  feature: Feature
}

const addressLocation = ref<AddressLocation>({ address: '' })
const suggestions = ref<Suggestion[]>([])
const showInput = ref(false)
const showSuggestions = ref(false)
const loading = ref(false)
const map = ref<Map>()
let marker: Marker | undefined

const defaultCenter: [number, number] = [6.142873, 46.205066]

const hasLocation = computed(() => addressLocation.value.lat && addressLocation.value.lon)

onMounted(onInit)

function onInit() {
  addressLocation.value = props.modelValue || { address: '' }
  suggestions.value = []
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
    addressLocation.value.lat = e.lngLat.lat
    addressLocation.value.lon = e.lngLat.lng
    addressLocation.value.address = undefined
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
  if (addressLocation.value.lat && addressLocation.value.lon) {
    marker = new Marker().setLngLat([addressLocation.value.lon, addressLocation.value.lat])
    marker.addTo(map.value)
    map.value.flyTo({
      center: [addressLocation.value.lon, addressLocation.value.lat], // New center
      zoom: map.value.getZoom(),
      speed: 2, // Control the animation speed (default: 1.2)
      curve: 1, // Control the smoothness of the curve
      essential: true, // Makes it non-disruptive for screen readers
    })
    showInput.value = false
  }
}

function onUpdate() {
  emit('update:modelValue', addressLocation.value)
}

function onSuggestAddress() {
  if (addressLocation.value?.address === undefined || addressLocation.value.address.length < 3) {
    return
  }
  loading.value = true
  showSuggestions.value = false
  suggestions.value = []
  geocoderApi
    .forwardGeocode({ query: addressLocation.value.address, limit: 10 })
    .then((collection) => {
      if (collection && collection.features && collection.features.length) {
        suggestions.value = collection.features
          .filter((feature) => feature.properties?.address)
          .map((feature) => ({ value: toAddress(feature), feature }))
      }
    })
    .catch((error) => {
      console.error(error)
    })
    .finally(() => {
      showSuggestions.value = true
      loading.value = false
    })
}

function onSuggestionSelected(suggestion: Suggestion) {
  addressLocation.value.address = suggestion.value
  showSuggestions.value = false

  addressLocation.value.lat = (suggestion.feature.geometry as Point).coordinates[1]
  addressLocation.value.lon = (suggestion.feature.geometry as Point).coordinates[0]

  onUpdateMarker()
  onUpdate()
}

function onRemoveLocation() {
  addressLocation.value.lat = undefined
  addressLocation.value.lon = undefined
  addressLocation.value.address = ''
  onUpdateMarker()
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
