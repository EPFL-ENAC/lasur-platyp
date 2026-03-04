<template>
  <div class="title q-mb-md">{{ props.title }}</div>
  <div>
    <div v-if="!hasData" class="no-data">
      {{ t('stats.no_data') }}
    </div>
    <location-heatmap
      v-else
      :data="data"
      :center="[7.4474, 46.9481]"
      :zoom="5"
      :height="`${props.height}px`"
      :map-id="id"
    />
  </div>
</template>

<script setup lang="ts">
import LocationHeatmap from '../LocationHeatmap.vue'

const { t } = useI18n()
const stats = useStats()

interface Props {
  kind: 'home' | 'workplace'
  title: string
  height?: number
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

const id = ref(`location-heatmap-${props.kind}-${crypto.randomUUID()}`)

const data = computed(() => {
  return props.kind === 'home' ? stats.homeLocationsHeatmap : stats.workplaceLocationsHeatmap
})

const hasData = computed(() => {
  return !!data.value && Object.keys(data.value).length > 0
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