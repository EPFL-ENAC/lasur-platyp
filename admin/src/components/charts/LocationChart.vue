<template>
  <div class="text-h6 text-center q-mb-md">{{ props.title }}</div>
  <div class="wrapper">
     <div v-if="!hasData" class="text-subtitle1 text-foreground text-center">
      {{ t('stats.no_data') }}
    </div>
    <div v-else class="with-data">
      <location-heatmap
        :h3Heatmap="stats.homeLocationsHeatmap"
        :dots="stats.workplaceLocations"
        :heatmap-gradient="gradient"
        :center="[7.4474, 46.9481]"
        :zoom="5"
        :fit-bounds-margins="2"
        :height="`${props.height}px`"
        :map-id="id"
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
  </div>
</template>

<script setup lang="ts">
import { GradientScale } from 'src/utils/colors'
import LocationHeatmap from '../LocationHeatmap.vue'
import { getRandomId } from 'src/utils/random'

const { t } = useI18n()
const stats = useStats()

interface Props {
  title: string
  height?: number
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

const gradient = computed(() => {
  const maxValue = max.value
  return new GradientScale([
    { value: 0, color: '#440154' }, // Dark Purple (Low)
    { value: maxValue * 0.25, color: '#3b528b' }, // Blue
    { value: maxValue * 0.5, color: '#21918c' }, // Teal/Green
    { value: maxValue * 0.75, color: '#5ec962' }, // Light Green
    { value: maxValue, color: '#fde725' }, // Yellow (High)
  ])
})

const id = ref(`location-heatmap-${getRandomId()}`)

const hasData = computed(() => {
  const hasHeatmapData =
    !!stats.homeLocationsHeatmap && Object.keys(stats.homeLocationsHeatmap).length > 0
  const hasWorkplaceData = !!stats.workplaceLocations && stats.workplaceLocations.length > 0
  return hasHeatmapData || hasWorkplaceData
})

const max = computed(() => {
  if (!stats.homeLocationsHeatmap) return 0

  const values = Object.values(stats.homeLocationsHeatmap)
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
