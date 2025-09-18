<template>
  <q-page>
    <div class="text-h5 q-pa-md row">
      <q-breadcrumbs gutter="sm">
        <q-breadcrumbs-el :label="t('records')" to="/records" />
        <q-breadcrumbs-el :label="record?.token" />
      </q-breadcrumbs>
    </div>
    <q-separator />
    <div class="q-pa-md">
      <div>
        <div class="text-h6 q-mb-sm">{{ t('record.isochrones') }}</div>
        <div class="text-help q-mb-md">{{ t('record.isochrones_hint') }}</div>
        <div class="text-help q-mb-md">
          {{ t('record.reco', { mode: reco }) }}
        </div>
        <IsochronesMap
          v-if="record && reco && origin"
          :mapId="`map-record-${record.id}`"
          :center="origin"
          :reco="reco"
          :height="'600px'"
          :zoom="11"
        />
      </div>
      <pre>{{ record }}</pre>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import IsochronesMap from 'src/components/IsochronesMap.vue'
import type { Record } from 'src/models'

interface Location {
  lat: number
  lon: number
}

const route = useRoute()
const { t } = useI18n()
const services = useServices()
const service = services.make('record') as Service<Record>

const id = computed(() => route.params.id)
const record = ref<Record>()

const origin = computed(() => {
  if (record.value?.data?.origin) {
    const orig = record.value.data.origin as unknown as Location
    return [orig.lon, orig.lat] as [number, number]
  }
  return undefined
})

const reco = computed(() => {
  const recommendations = (record.value?.typo?.reco?.reco_dt2 as string[]) || []
  return recommendations.length > 0 ? recommendations[0] : undefined
})

onMounted(() => {
  if (id.value === undefined) return
  onInit()
})

function onInit() {
  service.get(id.value + '').then((data: Record) => {
    record.value = data
  })
}
</script>
