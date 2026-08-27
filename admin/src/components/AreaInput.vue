<template>
  <div>
    <div class="map" ref="mapContainer"></div>
    <div class="box-info">
      <q-icon name="info" size="md" class="q-mr-sm" />
      <div>
        <div>
          {{ t('boundary_select.hint') }}
        </div>
        <div>
          {{ t('boundary_select.zoom_hint') }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Map, Marker } from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { style } from '@/utils/maps'
import type { Position } from 'geojson'
import type { PlaceLocation } from '@/components/models'
import { BoundariesManager } from '@/utils/boundaries'

interface Props {
  modelValue?: GeoJSON.FeatureCollection | undefined
  center?: [number, number] | undefined
  zoom?: number | undefined
  points?: Position[] | undefined
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const { t } = useI18n()

const mapContainer = ref<HTMLDivElement>()
const map = ref<maplibregl.Map>()

/**
 * The selected boundary's level/feature_id/lat/lon are carried in the emitted
 * feature's properties so that a previously selected boundary can be
 * re-highlighted when this component is remounted with the same modelValue.
 */
function toInitSelection(
  modelValue: GeoJSON.FeatureCollection | undefined,
): PlaceLocation | undefined {
  const properties = modelValue?.features[0]?.properties as
    | Partial<PlaceLocation>
    | null
    | undefined
  const { level, feature_id, lat, lon } = properties || {}
  if (level === undefined || feature_id === undefined || lat === undefined || lon === undefined) {
    return undefined
  }
  return { level, feature_id, lat, lon }
}

function toFeatureCollection(
  selection: PlaceLocation | undefined,
  boundaries: BoundariesManager,
): GeoJSON.FeatureCollection | undefined {
  if (!selection || selection.feature_id === undefined) return undefined
  const geometry = boundaries.getBoundaryGeometry(selection.level, selection.feature_id)
  if (!geometry) return undefined
  return {
    type: 'FeatureCollection',
    features: [{ type: 'Feature', geometry, properties: { ...selection } }],
  }
}

onMounted(() => {
  let center: [number, number] = [6.1432, 46.2044] // geneva
  const initSelection = toInitSelection(props.modelValue)
  if (initSelection) {
    center = [initSelection.lon, initSelection.lat]
  } else if (props.center) {
    center = [props.center[0], props.center[1]]
  }

  // Initialize map
  map.value = new Map({
    container: mapContainer.value as HTMLDivElement,
    style: style,
    center: center,
    zoom: props.zoom || 8,
  })

  map.value.on('load', () => {
    if (map.value) {
      const boundaries = new BoundariesManager(map.value, initSelection, (selection) => {
        emit('update:modelValue', toFeatureCollection(selection, boundaries))
      })
    }
  })

  // Add marker for each point
  if (props.points) {
    props.points.forEach((point) => {
      new Marker()
        .setLngLat([point[0] as number, point[1] as number])
        .addTo(map.value as maplibregl.Map)
    })
  }
})

onUnmounted(() => {
  if (map.value) {
    map.value.remove()
  }
})
</script>

<style scoped>
.map {
  height: 500px;
  width: 100%;
}

.box-info {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
</style>
