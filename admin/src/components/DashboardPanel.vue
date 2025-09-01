<template>
  <div>
    <div class="text-h5 q-mb-sm">{{ t('statistics') }}</div>
    <div class="row q-col-gutter-md q-mb-md">
      <q-select
        filled
        dense
        multiple
        emit-value
        map-options
        use-chips
        v-model="companyFilter"
        :label="t('companies')"
        :options="companyOptions"
        style="min-width: 200px"
        @update:model-value="onFilter"
      />
      <q-select
        filled
        dense
        multiple
        emit-value
        map-options
        use-chips
        v-model="campaignFilter"
        :label="t('campaigns')"
        :options="campaignOptions"
        style="min-width: 200px"
        @update:model-value="onFilter"
      />
    </div>
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
      <div class="text-h6 q-mt-md q-mb-md">{{ t('stats.freq_mod') }}</div>
      <div>{{ stats.frequencies.freq_mod }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Company, Campaign } from 'src/models'
import type { Filter } from 'src/components/models'
const { t } = useI18n()
const stats = useStats()
const services = useServices()
const companyService = services.make('company')
const campaignService = services.make('campaign')

const companyMap = ref<{ [key: string]: Company }>({})
const campaignMap = ref<{ [key: string]: Campaign }>({})

const companyFilter = ref<string[]>([])
const companyOptions = computed(() => {
  return Object.values(companyMap.value)
    .map((company) => ({
      label: company.name,
      value: company.id,
    }))
    .sort((a, b) => a.label.localeCompare(b.label))
})

const campaignFilter = ref<string[]>([])
const campaignOptions = computed(() => {
  return Object.values(campaignMap.value)
    .map((campaign) => ({
      label: `${getCompanyName(campaign.company_id)} - ${campaign.name}`,
      value: campaign.id,
    }))
    .sort((a, b) => a.label.localeCompare(b.label))
})

onMounted(() => {
  stats.loadStats()
  companyService.find({ $limit: 1000, $select: ['id', 'name'] }).then((result) => {
    const companies = result.data
    companies.forEach((company: Company) => {
      companyMap.value[`${company.id}`] = company
    })
  })
  campaignService.find({ $limit: 1000, $select: ['id', 'name', 'company_id'] }).then((result) => {
    const campaigns = result.data
    campaigns.forEach((campaign: Campaign) => {
      campaignMap.value[`${campaign.id}`] = campaign
    })
  })
})

function getCompanyName(companyId: string | number | undefined): string {
  return companyMap.value[`${companyId}`]?.name || `${companyId}`
}

function onFilter() {
  const query = {} as Filter
  if (companyFilter.value.length > 0) {
    query.company_id = { $in: companyFilter.value }
  }
  if (campaignFilter.value.length > 0) {
    query.campaign_id = { $in: campaignFilter.value }
  }
  stats.loadStats(query)
}
</script>
