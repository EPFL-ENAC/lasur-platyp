<template>
  <div class="map-container" :style="`--t-height: ${height || '400px'}`">
    <div ref="mapEl" class="mapview"></div>

    <q-btn
      v-if="selected"
      class="map-reset"
      dense
      unelevated
      size="sm"
      color="grey-8"
      icon="close"
      :label="t('stats.locations_heatmap.reset_selection')"
      @click="reset"
    />

    <!-- Legend Overlay -->
    <div class="map-legend">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  AttributionControl,
  FullscreenControl,
  LngLatBounds,
  Map as MaplibreMap,
  NavigationControl,
  type GeoJSONSource,
} from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { style } from '@/utils/maps'
import { cellToBoundary } from 'h3-js'
import type { GradientScale } from '@/utils/colors'
import type { H3Heatmap, HomeWorkplaceFlow, WorkplaceLocation } from '@/models'
import { useMapSelection } from '@/composables/useMapSelection'

interface HeatmapGeoJSON {
  shape: GeoJSON.FeatureCollection<GeoJSON.Polygon, { value: number; hexId: string }>
  workplaces: GeoJSON.FeatureCollection<GeoJSON.Point, { id: number }>
  boundingBox: LngLatBounds
}

interface Props {
  h3Heatmap: H3Heatmap
  workplaces: WorkplaceLocation[]
  flows: HomeWorkplaceFlow[]
  heatmapGradient: GradientScale
  center: [number, number]
  height?: string
  zoom?: number
  fitBoundsMargins: number
  noControls?: boolean
  interactive?: boolean
}
const props = defineProps<Props>()

const { t } = useI18n()

const mapEl = useTemplateRef<HTMLDivElement>('mapEl')

defineExpose({
  exportImage,
  mapEl,
})

// Slight tilt so the flow arcs read as 3D without distorting the basemap
const MAP_PITCH = 30

const map = ref<MaplibreMap>()

// Clicking a workplace or home hexagon selects it and filters the map to its flows
const { selected, addInteractions, onKeydown, reset, getArcsCanvas, closePopup } = useMapSelection({
  map,
  workplaces: () => props.workplaces,
  flows: () => props.flows,
  heatmap: () => props.h3Heatmap,
  gradient: () => props.heatmapGradient,
  t,
})

onMounted(() => {
  onInit()
  if (props.interactive) window.addEventListener('keydown', onKeydown)
})
onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  if (map.value) {
    map.value.remove()
    map.value = undefined
  }
})

watch([() => props.h3Heatmap, () => props.workplaces, () => props.flows], () => {
  reset()
  if (map.value) {
    const source = map.value.getSource('heatmap-data') as GeoJSONSource
    const workplaceSource = map.value.getSource('workplace-data') as GeoJSONSource
    if (source) {
      const geoJson = makeGeoJSON()
      source.setData(geoJson.shape)
      if (workplaceSource) {
        workplaceSource.setData(geoJson.workplaces)
      }
      map.value.fitBounds(geoJson.boundingBox, {
        padding: props.fitBoundsMargins,
        pitch: MAP_PITCH,
        duration: 500,
      })
    }
  }
})

function makeGeoJSON(): HeatmapGeoJSON {
  const boundingBox = new LngLatBounds()
  const shape: HeatmapGeoJSON['shape'] = {
    type: 'FeatureCollection',
    features: Object.entries(props.h3Heatmap).map(([hexId, value]) => {
      const boundary = cellToBoundary(hexId, true)
      boundary.forEach((coord) => boundingBox.extend(coord))

      return {
        type: 'Feature',
        geometry: {
          type: 'Polygon',
          coordinates: [boundary],
        },
        properties: {
          value,
          hexId,
        },
      }
    }),
  }

  const workplaceFeatures: GeoJSON.Feature<GeoJSON.Point, { id: number }>[] = props.workplaces.map(
    (wp) => {
      boundingBox.extend([wp.lon, wp.lat])
      return {
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: [wp.lon, wp.lat],
        },
        properties: { id: wp.id },
      }
    },
  )

  return {
    shape,
    workplaces: {
      type: 'FeatureCollection',
      features: workplaceFeatures,
    },
    boundingBox,
  }
}

function onInit() {
  if (!mapEl.value) return

  map.value = new MaplibreMap({
    container: mapEl.value,
    center: props.center,
    style: style,
    trackResize: true,
    zoom: props.zoom || 14,
    pitch: MAP_PITCH,
    attributionControl: false,
    canvasContextAttributes: {
      preserveDrawingBuffer: true, // This is needed to be able to export the map as an image
    },
  })
  if (!props.noControls) {
    map.value.addControl(new NavigationControl({ visualizePitch: true }))
    map.value.addControl(new FullscreenControl({}))
  }
  map.value.addControl(
    new AttributionControl({
      compact: true,
      customAttribution:
        '© <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>',
    }),
  )

  map.value.on('load', () => {
    if (!map.value) return
    addLayers(map.value)
    if (props.interactive) addInteractions(map.value)
    map.value.fitBounds(makeGeoJSON().boundingBox, {
      padding: props.fitBoundsMargins,
      pitch: MAP_PITCH,
      duration: 500,
    })
  })

  map.value.resize()
}

function addLayers(m: MaplibreMap) {
  const geoJson = makeGeoJSON()
  m.addSource('heatmap-data', {
    type: 'geojson',
    data: geoJson.shape,
  })
  m.addLayer({
    id: 'heatmap-layer',
    type: 'fill',
    source: 'heatmap-data',
    paint: {
      // Color the hexagons based on the 'value' property
      'fill-color': props.heatmapGradient.toMapLibreExpression('value'),
      'fill-opacity': 0.6,
      'fill-outline-color': '#ffffff',
    },
  })

  m.addSource('workplace-data', {
    type: 'geojson',
    data: geoJson.workplaces,
  })
  m.addLayer({
    id: 'workplace-dots',
    type: 'circle',
    source: 'workplace-data',
    paint: {
      'circle-radius': 5,
      'circle-color': '#EF4444',
      'circle-stroke-width': 2,
      'circle-stroke-color': '#FFFFFF',
    },
  })
}

function exportImage(): Promise<string | null> {
  return new Promise((resolve) => {
    if (!map.value) {
      resolve(null)
      return
    }
    closePopup()
    map.value.once('render', () => {
      const canvas = map.value?.getCanvas()
      if (canvas) {
        resolve(compositeArcs(canvas).toDataURL('image/png'))
      } else {
        resolve(null)
      }
    })
    map.value?.triggerRepaint() // Force a repaint to ensure the 'render' event is fired
  })
}

/** The arcs are drawn on deck.gl's own canvas: paint them over the map canvas for export. */
function compositeArcs(mapCanvas: HTMLCanvasElement): HTMLCanvasElement {
  const arcs = getArcsCanvas()
  if (!arcs) return mapCanvas
  const output = document.createElement('canvas')
  output.width = mapCanvas.width
  output.height = mapCanvas.height
  const ctx = output.getContext('2d')
  if (!ctx) throw new Error('2D canvas context unavailable for map export')
  ctx.drawImage(mapCanvas, 0, 0)
  ctx.drawImage(arcs, 0, 0, output.width, output.height)
  return output
}
</script>

<style scoped>
.map-container {
  position: relative;
  width: 100%;
  height: var(--t-height);
}

.mapview {
  width: 100%;
  height: 100%;
}

.map-reset {
  position: absolute;
  top: 0.5rem;
  left: 0.5rem;
  z-index: 2;
}

.map-legend {
  position: absolute;
  bottom: 0.5rem;
  left: 0.5rem;
  z-index: 2;
  background: white;
  padding: 12px;
  border-radius: 4px;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
  font-family: sans-serif;
  font-size: 12px;
  color: #333;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 150px;
}

/* The deck.gl arc canvas is mounted as a map control (z-index 2): keep the tooltip above it */
.map-container :deep(.maplibregl-popup) {
  z-index: 3;
}

.map-container :deep(.map-tooltip) {
  font-family: sans-serif;
  font-size: 12px;
  color: #333;
  max-width: 240px;
}

.map-container :deep(.map-tooltip-title) {
  font-weight: bold;
  margin-bottom: 4px;
}

.map-container :deep(.map-tooltip-count) {
  margin-top: 4px;
  color: #666;
}
</style>
