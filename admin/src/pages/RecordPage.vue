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
      <pre>{{ record }}</pre>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import type { Record } from 'src/models'

const route = useRoute()
const { t } = useI18n()
const services = useServices()
const service = services.make('record') as Service<Record>

const id = computed(() => route.params.id)
const record = ref<Record>()

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
