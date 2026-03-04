<template>
  <div class="title q-mb-md">{{ t('stats.homeLocationHeatmap.title') }}</div>
  <div>
    <div v-if="!hasData" class="no-data">
      {{ t('stats.no_data') }}
    </div>
    <location-heatmap
      v-else
      :data="stats.homeLocationsHeatmap"
      :center="[7.4474, 46.9481]"
      :zoom="5"
      :height="`${props.height}px`"
      map-id="home-locations-heatmap"
    />
  </div>
</template>

<script setup lang="ts">
import LocationHeatmap from '../LocationHeatmap.vue'

const { t } = useI18n()
const stats = useStats()

interface Props {
  height?: number
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

const hasData = computed(() => {
  return !!stats.homeLocationsHeatmap && Object.keys(stats.homeLocationsHeatmap).length > 0
})
</script>

<style scoped>

.title {
  font-size: 16px;
  font-weight: 600;
  color: #454545;
  text-align: center;
}

</style>