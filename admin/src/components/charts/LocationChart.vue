<template>
  <div class="title q-mb-md">{{ props.title }}</div>
  <div>
    <div v-if="!hasData" class="no-data">
      {{ t('stats.no_data') }}
    </div>
    <div v-else class="with-data">
      <div class="toolbar q-pa-sm">
        <q-btn-toggle
          v-model="kind"
          :options="[
            { label: t('stats.locationsHeatmap.home'), value: 'home' },
            { label: t('stats.locationsHeatmap.workplace'), value: 'workplace' },
            { label: t('stats.locationsHeatmap.all'), value: 'all' },
          ]"
          toggle-color="primary"
          color="white"
          text-color="black"
          size="sm"
          class="q-mb-md"
        />
      </div>
      <location-heatmap
        :data="data"
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

const kind = ref<'home' | 'workplace' | 'all'>('all')

const id = ref(`location-heatmap-${crypto.randomUUID()}`)

const data = computed(() => {
  if (kind.value === 'home') {
    return stats.homeLocationsHeatmap
  } else if (kind.value === 'workplace') {
    return stats.workplaceLocationsHeatmap
  }
  
  return stats.allLocationsHeatmap
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

.with-data {
  position: relative;
}

.toolbar {
  position: absolute;
  top: 0;
  z-index: 100;
}

</style>