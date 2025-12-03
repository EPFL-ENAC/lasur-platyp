<template>
  <div>
    <div class="map" ref="mapContainer"></div>
    <div class="row q-mt-md">
      <q-icon name="info" size="xs" class="q-mr-sm" />
      <span>
        {{ t(`draw_mode.${drawMode}_hint`) }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Map } from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import MaplibreGlDraw from 'maplibre-gl-draw'
import 'maplibre-gl-draw/dist/mapbox-gl-draw.css'
import { style } from 'src/utils/maps'

interface Props {
  modelValue?: GeoJSON.FeatureCollection | undefined
  center?: [number, number] | undefined
  zoom?: number | undefined
}
const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const { t } = useI18n()

const mapContainer = ref<HTMLDivElement>()
const map = ref<maplibregl.Map>()
const draw = ref<MaplibreGlDraw>()
const drawMode = ref<string>('simple_select')

onMounted(() => {
  // Initialize map
  map.value = new Map({
    container: mapContainer.value as HTMLDivElement,
    style: style,
    center: props.center || [6.1432, 46.2044], // geneva
    zoom: props.zoom || 8,
  })

  draw.value = new MaplibreGlDraw({
    displayControlsDefault: false,
    controls: {
      polygon: true,
      trash: true,
    },
  })
  // @ts-expect-error - Type mismatch between maplibre-gl-draw and maplibre-gl types
  map.value.addControl(draw.value)

  // Get polygon created
  map.value.on('draw.create', () => {
    emit('update:modelValue', draw.value?.getAll())
  })

  // Update polygon
  map.value.on('draw.update', () => {
    emit('update:modelValue', draw.value?.getAll())
  })

  // Delete polygon
  map.value.on('draw.delete', () => {
    emit('update:modelValue', draw.value?.getAll())
  })

  // Track mode changes
  map.value.on('draw.modechange', (e) => {
    drawMode.value = e.mode

    if (e.mode === 'draw_polygon') {
      // Delete existing valid polygons when entering draw mode
      const allFeatures = draw.value?.getAll()
      if (allFeatures && allFeatures.features.length > 1) {
        allFeatures.features.forEach((feature) => {
          if (isValidPolygon(feature)) {
            draw.value?.delete(feature.id as string)
          }
        })
        emit('update:modelValue', draw.value?.getAll())
      }
    }
  })
})

onUnmounted(() => {
  if (map.value) {
    map.value.remove()
  }
})

function isValidPolygon(feature: GeoJSON.Feature | undefined): boolean {
  if (feature?.geometry.type === 'Polygon') {
    // check it is not the one being drawn
    const coordinates = (feature.geometry as GeoJSON.Polygon).coordinates
    if (coordinates.length > 0) {
      const firstPosition = coordinates[0]
      if (firstPosition && firstPosition.length > 0 && firstPosition[0] !== null) {
        return true
      }
    }
    return false
  }
  return false
}
</script>

<style scoped>
.map {
  height: 500px;
  width: 100%;
}
</style>
