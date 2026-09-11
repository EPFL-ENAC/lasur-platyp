<template>
  <chart-panel
    :title="t('stats.locations_heatmap.title')"
    :description="t('stats.locations_heatmap.description')"
    :inline="inline"
  >
    <q-toolbar v-if="!inline" class="chart-toolbar">
      <q-space />
      <q-btn flat icon="more_vert">
        <q-menu>
          <q-list style="min-width: 200px">
            <q-item clickable v-close-popup @click="onChartDownload">
              <q-item-section side>
                <q-icon name="download" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ t('download') }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-menu>
      </q-btn>
    </q-toolbar>
    <chart-shell
      ref="shellRef"
      :height="height"
      :loading="!hasData"
      :has-data="hasData"
      :show-info="hasData"
      :no-data-title="t('stats.locations_heatmap.title')"
      :no-data-text="t('stats.no_data')"
      :exportable="!inline"
      :capture-raw-image="captureRawImage"
    >
      <div ref="wrapper">
        <div class="title text-center q-mb-md">{{ t('stats.locations_heatmap.title') }}</div>
        <location-heatmap
          ref="heatmap"
          :h3Heatmap="props.homeLocationsHeatmap"
          :workplaces="props.workplaceLocations"
          :flows="props.homeWorkplaceFlows"
          :campaign-colors="campaignColors"
          :interactive="!props.inline"
          :heatmap-gradient="gradient"
          :center="[7.4474, 46.9481]"
          :zoom="5"
          :fit-bounds-margins="2"
          :height="mapHeight"
          :no-controls="props.noControls"
        >
          <div v-if="groups.length === 0" class="legend-item">
            <span class="legend-swatch dot"></span>
            <span class="legend-label">{{ t('stats.locations_heatmap.workplaces') }}</span>
          </div>
          <div v-for="(group, i) in groups" :key="group.name" class="legend-item">
            <span class="legend-swatch dot" :style="{ backgroundColor: groupColor(i) }"></span>
            <span class="legend-label">
              {{
                t('stats.locations_heatmap.group_workplaces', {
                  group: t(`stats.group.${group.name}`),
                })
              }}
            </span>
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
            <span class="legend-label">{{ t('stats.locations_heatmap.households') }}</span>
          </div>
          <div class="legend-item">
            <span
              class="legend-swatch line"
              :style="{ background: `linear-gradient(to right, ${gradient.colorAt(0)}, #ef4444)` }"
            ></span>
            <span class="legend-label">{{ t('stats.locations_heatmap.flows') }}</span>
          </div>
          <div>
            <div class="text-hint">
              <span class="legend-label">{{ t('stats.locations_heatmap.households_number') }}</span>
            </div>
            <div class="gradient-container">
              <div
                class="gradient-bar"
                :style="{ background: gradient.toCSSGradient('to right') }"
              ></div>
              <div class="gradient-labels">
                <span>1</span>
                <span>{{ max }}</span>
              </div>
            </div>
          </div>
        </location-heatmap>
      </div>
    </chart-shell>
  </chart-panel>
</template>
<script setup lang="ts">
import ChartPanel from './ChartPanel.vue'
import html2canvas from 'html2canvas'
import type { Ref } from 'vue'
import { GradientScale } from '@/utils/colors'
import ChartShell from './ChartShell.vue'
import LocationHeatmap from '../LocationHeatmap.vue'
import { GROUP_COLORS } from './commons'
import type { H3Heatmap, HomeWorkplaceFlow, WorkplaceLocation } from '@/models'

const { t } = useI18n()
const stats = useStats()

// In a comparison, dots take the colour of the group their campaign belongs to
const groups = computed(() => stats.comparisonResults?.groups ?? [])

function groupColor(index: number): string {
  return GROUP_COLORS[index % GROUP_COLORS.length] ?? '#ccc'
}

const campaignColors = computed<Record<number, string>>(() =>
  Object.fromEntries(
    groups.value.flatMap((group, i) => group.campaign_ids.map((id) => [id, groupColor(i)])),
  ),
)

interface Props {
  homeLocationsHeatmap: H3Heatmap
  workplaceLocations: WorkplaceLocation[]
  homeWorkplaceFlows: HomeWorkplaceFlow[]
  height?: number
  noControls?: boolean
  inline?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  height: 400,
  noControls: false,
  exportable: true,
})

const mapHeight = computed(() => `${props.height - 50}px`)

type LocationHeatmapExposed = {
  exportImage: () => Promise<string | null>
  mapEl: Ref<HTMLDivElement | undefined>
}

type ChartShellExposed = {
  handleExport: () => Promise<void>
}

const heatmap = useTemplateRef<LocationHeatmapExposed>('heatmap')
const wrapper = useTemplateRef<HTMLDivElement>('wrapper')
const shellRef = useTemplateRef<ChartShellExposed>('shellRef')

function onChartDownload() {
  shellRef.value?.handleExport()
}

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
  const mapRootEl = heatmap.value.mapEl.value

  if (!mapRootEl) {
    console.warn('captureRawImage: map root not found')
    return null
  }

  // MapLibre's map root is only a template ref and has no id, so html2canvas's
  // onclone can't find it via getElementById. Assign a stable id just for the
  // clone lookup, then restore it afterwards.
  const MAP_ROOT_ID = 'map-root-export'
  const previousId = mapRootEl.id
  mapRootEl.id = MAP_ROOT_ID

  const mapImageUrl = await heatmap.value.exportImage()
  if (!mapImageUrl) {
    mapRootEl.id = previousId
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
        const clonedMapRoot = clonedDocument.getElementById(MAP_ROOT_ID)
        if (!clonedMapRoot) return

        // Hide MapLibre-rendered parts only, keep legend visible.
        const mapCanvasContainers = clonedMapRoot.querySelectorAll(
          '.maplibregl-canvas-container, .maplibregl-control-container, .map-reset',
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
  } finally {
    mapRootEl.id = previousId
  }
}

const gradient = computed(() => {
  const maxValue = max.value
  // Single-hue pastel blues, near white (sparse) → darker blue (dense)
  return new GradientScale([
    { value: 0, color: '#eef3fb' },
    { value: maxValue * 0.25, color: '#c5d6ef' },
    { value: maxValue * 0.5, color: '#92b2df' },
    { value: maxValue * 0.75, color: '#5d88c6' },
    { value: maxValue, color: '#2f5c9d' },
  ])
})

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

.legend-swatch.line {
  height: 3px;
  border-radius: 2px;
  align-self: center;
}

.gradient-container {
  margin-top: 0;
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
