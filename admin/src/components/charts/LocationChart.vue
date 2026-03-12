<template>
  <div class="title q-mb-md">{{ props.title }}</div>
  <div>
    <div v-if="!hasData" class="no-data">
      {{ t('stats.no_data') }}
    </div>
    <div v-else class="with-data">
      <location-heatmap
        :data="stats.homeLocationsHeatmap"
        :workplaces="stats.workplaceLocations"
        :center="[7.4474, 46.9481]"
        :zoom="5"
        :height="`${props.height}px`"
        :map-id="id"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import LocationHeatmap from '../LocationHeatmap.vue'

const { t } = useI18n()
const stats = useStats()

interface Props {
  title: string
  height?: number
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

const id = ref(`location-heatmap-${crypto.randomUUID()}`)

const hasData = computed(() => {
  const hasHeatmapData = !!stats.homeLocationsHeatmap && Object.keys(stats.homeLocationsHeatmap).length > 0
  const hasWorkplaceData = !!stats.workplaceLocations && stats.workplaceLocations.length > 0
  return hasHeatmapData || hasWorkplaceData
})
</script>

<style scoped>

.title {
  font-size: 16px;
  font-weight: 600;
  color: #454545;
  text-align: center;
}

.with-data {
  position: relative;
}

.toolbar {
  position: absolute;
  top: 0;
  z-index: 100;
}

</style>