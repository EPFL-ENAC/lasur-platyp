<template>
  <q-page>
    <div class="text-h5 q-pa-md">{{ t('dashboard') }}</div>
    <q-separator />
    <div class="bg-info text-white q-pt-sm q-pb-sm q-pl-md q-pr-md">
      {{
        t('your_role', { role: t(authStore.isAdmin ? 'role.platyp-admin' : 'role.platyp-user') })
      }}
    </div>
    <div class="q-pa-md">
      <div class="text-h5 q-mb-sm">{{ t('statistics') }}</div>
      <q-select
        filled
        dense
        v-model="selectedCompany"
        :options="companyOptions"
        :label="t('stats.filter_by_company')"
        clearable
        @update:model-value="onCompanyChange"
        class="q-mb-md"
        style="max-width: 300px"
      />
      <div v-if="stats.loading">
        <q-spinner-dots size="md" color="primary" />
      </div>
      <div v-else>
        <div class="text-h6 q-mb-md">{{ t('stats.equipments') }}</div>
        <div>{{ stats.frequencies.equipments }}</div>
        <div class="text-h6 q-mt-md q-mb-md">{{ t('stats.constraints') }}</div>
        <div>{{ stats.frequencies.constraints }}</div>
        <div class="text-h6 q-mt-md q-mb-md">{{ t('stats.travel_time') }}</div>
        <div>{{ stats.frequencies.travel_time }}</div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import type { Query } from 'src/components/models'
import type { Company } from 'src/models'
const { t } = useI18n()
const authStore = useAuthStore()
const stats = useStats()
const services = useServices()
const service = services.make('company')

const companies = ref<Company[]>([])
const selectedCompany = ref<{ label: string; value: number } | null>(null)

const companyOptions = computed(() =>
  companies.value.map((company: Company) => ({
    label: company.name,
    value: company.id,
  })),
)

onMounted(() => {
  stats.loadStats()
  const query: Query = {
    // Define your query here
    $select: ['id', 'name'],
  }
  service
    .find(query)
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    .then((result: any) => {
      companies.value = result.data
      return result
    })
})

function onCompanyChange() {
  console.log('Selected company:', selectedCompany.value)
  if (selectedCompany.value) {
    stats.loadStats({ company_id: { $in: [selectedCompany.value.value] } })
  } else {
    stats.loadStats()
  }
}
</script>
