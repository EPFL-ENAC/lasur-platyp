<template>
  <q-page>
    <div class="text-h5 q-pa-md">
      <q-breadcrumbs gutter="sm">
        <q-breadcrumbs-el :label="t('companies')" to="/companies" />
        <q-breadcrumbs-el :label="company?.name" />
      </q-breadcrumbs>
    </div>
    <q-separator />
    <div class="q-pa-md">
      <pre>{{ company }}</pre>
      <div class="text-h6 q-mb-sm">{{ t('campaigns') }}</div>
      <company-campaigns v-if="company" :company="company" />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import type { Company } from 'src/models'
import type { Service } from 'src/stores/services'
import CompanyCampaigns from 'src/components/CompanyCampaigns.vue'

const route = useRoute()
const { t } = useI18n()
const services = useServices()
const service = services.make('company') as Service<Company>

const id = computed(() => route.params.id)
const company = ref<Company>()

onMounted(() => {
  if (id.value === undefined) return
  service.get(id.value + '').then((data: Company) => {
    company.value = data
  })
})
</script>
