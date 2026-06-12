<template>
  <chart-shell
    :height="height"
    :loading="!hasData"
    :has-data="hasData"
    :show-info="hasData"
    :no-data-title="props.title"
    :no-data-text="t('stats.no_data')"
    :exportable="!!exportable"
    :capture-raw-image="captureRawImage"
  >
    <div ref="wrapper">
      <div class="title text-center q-mb-md">{{ props.title }}</div>
      <location-heatmap
        ref="heatmap"
        :h3Heatmap="props.homeLocationsHeatmap"
        :dots="props.workplaceLocations"
        :heatmap-gradient="gradient"
        :center="[7.4474, 46.9481]"
        :zoom="5"
        :fit-bounds-margins="2"
        :height="mapHeight"
        :map-id="id"
        :no-controls="props.noControls"
      >
        <div class="legend-item">
          <span class="legend-swatch dot"></span>
          <span class="legend-label">{{ t('stats.locationsHeatmap.workplaces') }}</span>
        </div>
        <div class="legend-item">
          <span class="legend-swatch">
            <svg
              version="1.1"
              xmlns="http://www.w3.org/2000/svg"
              height="16"
              width="16"
              viewBox="0 0 726 628"
            >
              <polygon
                points="723,314 543,625.769145 183,625.769145 3,314 183,2.230855 543,2.230855 723,314"
                :fill="gradient.colorAt(0)"
                :stroke="gradient.colorAt(0)"
                stroke-width="4"
              />
            </svg>
          </span>
          <span class="legend-label">{{ t('stats.locationsHeatmap.households') }}</span>
        </div>
        <div class="gradient-container">
          <div
            class="gradient-bar"
            :style="{ background: gradient.toCSSGradient('to right') }"
          ></div>
          <div class="gradient-labels">
            <span>1</span>
            <span>>{{ max }}</span>
          </div>
        </div>
      </location-heatmap>
    </div>
  </chart-shell>
  <div class="wrapper">
    <div v-if="!hasData" class="text-subtitle1 text-foreground text-center">
      {{ t('stats.no_data') }}
    </div>
    <div v-else class="with-data"></div>
  </div>
</template>
<script setup lang="ts">
import html2canvas from 'html2canvas'
import { GradientScale } from 'src/utils/colors'
import ChartShell from './ChartShell.vue'
import LocationHeatmap from '../LocationHeatmap.vue'
import { getRandomId } from 'src/utils/random'
import type { H3Heatmap, LatLon } from 'src/models'

const { t } = useI18n()

interface Props {
  title: string
  homeLocationsHeatmap: H3Heatmap
  workplaceLocations: LatLon[]
  height?: number
  noControls?: boolean
  exportable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  height: 400,
  noControls: false,
  exportable: true,
})

const mapHeight = computed(() => `${props.height - 50}px`)

type LocationHeatmapExposed = {
  exportImage: () => Promise<string | null>
}

const heatmap = useTemplateRef<LocationHeatmapExposed>('heatmap')
const wrapper = useTemplateRef<HTMLDivElement>('wrapper')

function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve(img)
    img.onerror = reject
    img.src = src
  })
}

async function captureRawImage(): Promise<string | null> {
  if (!wrapper.value || !heatmap.value) {
    return null
  }

  await nextTick()

  const wrapperEl = wrapper.value
  const mapRootEl = document.getElementById(id.value)

  if (!mapRootEl) {
    console.warn('captureRawImage: map root not found')
    return null
  }

  const mapImageUrl = await heatmap.value.exportImage()
  if (!mapImageUrl) {
    return null
  }

  const wrapperRect = wrapperEl.getBoundingClientRect()
  const mapRect = mapRootEl.getBoundingClientRect()

  const mapOffsetX = mapRect.left - wrapperRect.left
  const mapOffsetY = mapRect.top - wrapperRect.top

  try {
    const overlayCanvas = await html2canvas(wrapperEl, {
      backgroundColor: null,
      useCORS: true,
      scale: window.devicePixelRatio || 2,
      logging: false,
      onclone: (clonedDocument) => {
        const clonedMapRoot = clonedDocument.getElementById(id.value)
        if (!clonedMapRoot) return

        // Hide MapLibre-rendered parts only, keep legend visible.
        const mapCanvasContainers = clonedMapRoot.querySelectorAll(
          '.maplibregl-canvas-container, .maplibregl-control-container',
        )

        mapCanvasContainers.forEach((el) => {
          ;(el as HTMLElement).style.visibility = 'hidden'
        })

        // Optional: ensure the map host itself stays transparent so only
        // title/legend/other DOM remain in the captured overlay.
        ;(clonedMapRoot as HTMLElement).style.background = 'transparent'
      },
    })

    const mapImage = await loadImage(mapImageUrl)

    const finalCanvas = document.createElement('canvas')
    finalCanvas.width = overlayCanvas.width
    finalCanvas.height = overlayCanvas.height

    const ctx = finalCanvas.getContext('2d')
    if (!ctx) {
      return null
    }

    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, finalCanvas.width, finalCanvas.height)

    const scaleX = overlayCanvas.width / wrapperRect.width
    const scaleY = overlayCanvas.height / wrapperRect.height

    ctx.drawImage(
      mapImage,
      mapOffsetX * scaleX,
      mapOffsetY * scaleY,
      mapRect.width * scaleX,
      mapRect.height * scaleY,
    )

    // Draw title + legend + other DOM on top
    ctx.drawImage(overlayCanvas, 0, 0)

    return finalCanvas.toDataURL('image/png')
  } catch (error) {
    console.error('captureRawImage failed:', error)
    return null
  }
}

const gradient = computed(() => {
  const maxValue = max.value
  return new GradientScale([
    { value: 0, color: '#440154' },
    { value: maxValue * 0.25, color: '#3b528b' },
    { value: maxValue * 0.5, color: '#21918c' },
    { value: maxValue * 0.75, color: '#5ec962' },
    { value: maxValue, color: '#fde725' },
  ])
})

const id = ref(`location-heatmap-${getRandomId()}`)

const hasData = computed(() => {
  const hasHeatmapData =
    !!props.homeLocationsHeatmap && Object.keys(props.homeLocationsHeatmap).length > 0
  const hasWorkplaceData = !!props.workplaceLocations && props.workplaceLocations.length > 0

  return hasHeatmapData || hasWorkplaceData
})

const max = computed(() => {
  if (!props.homeLocationsHeatmap) return 0

  const values = Object.values(props.homeLocationsHeatmap)
  if (values.length === 0) return 0

  return Math.max(...values)
})
</script>

<style scoped>
.wrapper {
  width: 100%;
}

.title {
  font-size: 16px;
  font-weight: bold;
  color: #454545;
  text-align: center;
}

:global(.body--dark .title) {
  color: var(--q-primary) !important;
}

.with-data {
  position: relative;
}

.toolbar {
  position: absolute;
  top: 0;
  z-index: 100;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-swatch {
  width: 16px;
  height: 16px;
  display: inline-block;
}

.legend-swatch.dot {
  background-color: #ef4444;
  border: 2px solid #fff;
  border-radius: 50%;
  width: 12px;
  height: 12px;
  margin-left: 2px;
}

.gradient-container {
  margin-top: 4px;
}

.gradient-bar {
  height: 12px;
  width: 100%;
  border-radius: 2px;
}

.gradient-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 4px;
  font-size: 10px;
  font-weight: bold;
}
</style>
