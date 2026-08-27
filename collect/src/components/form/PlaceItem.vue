<template>
  <div>
    <div v-if="label" class="text-bold q-mb-md" :class="labelClass || 'text-h4'">{{ label }}</div>
    <div v-if="hint" class="text-h6">{{ hint }}</div>
    <div class="bg-white">
      <div :id="mapId" :style="`--t-height: ${height || '400px'}`" class="mapinput" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { AttributionControl, FullscreenControl, Map, NavigationControl } from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { style } from '@/utils/maps'
import { BoundariesManager } from '@/utils/boundaries'
import type { PlaceLocation } from '@/models'

const { t } = useI18n()

interface Props {
  modelValue: PlaceLocation | undefined
  label?: string
  hint?: string
  height?: string
  center?: [number, number]
  zoom?: number
  mapId: string
  labelClass?: string
  readOnly?: boolean
}
const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: PlaceLocation | undefined]
}>()

const defaultCenter: [number, number] = [6.142873, 46.205066]

const map = ref<Map>()

onMounted(onInit)

function onInit() {
  let center = defaultCenter
  const initSelection = props.modelValue
  if (initSelection) {
    center = [initSelection.lon, initSelection.lat]
  } else if (props.center) {
    center = [props.center[0], props.center[1]]
  }
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
      customAttribution: `© <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>, <a href="https://eurogeographics.org/" target="_blank">${t('eurogeographics_attributions')}</a>, <a href="https://www.geoboundaries.org/" target="_blank">geoBoundaries</a>`,
    }),
  )

  const mapInstance = map.value
  if (mapInstance) {
    mapInstance.on('load', () => {
      new BoundariesManager(
        mapInstance,
        initSelection,
        props.readOnly
          ? undefined
          : (selection: PlaceLocation | undefined) => {
              emit('update:modelValue', selection)
            },
      )
    })
  }
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
