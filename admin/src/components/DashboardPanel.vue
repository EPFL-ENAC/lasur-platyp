<template>
  <div>
    <div class="text-h5 q-mb-sm">{{ t('statistics') }}</div>
    <div class="row q-col-gutter-md q-mb-lg">
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
      <div class="row q-col-gutter-md">
        <div class="col">
          <frequencies-chart type="equipments" class="q-mb-md" />
        </div>
        <div class="col">
          <frequencies-chart type="constraints" class="q-mb-md" />
        </div>
      </div>
      <div class="row q-col-gutter-md">
        <div class="col">
          <frequencies-chart
            type="travel_time"
            :xaxis="t('stats.travel_time.xaxis')"
            :range-step="5"
            class="q-mb-md"
          />
        </div>
        <div class="col">
          <share-chart type="freq_mod" class="q-mb-md" />
        </div>
      </div>
      <div class="row q-col-gutter-md">
        <div class="col">
          <div class="text-h6 q-mt-md q-mb-md">{{ t('stats.freq_mod_pro.title') }}</div>
          <div>{{ stats.frequencies.freq_mod_pro }}</div>
        </div>
        <div class="col">
          <div class="text-h6 q-mt-md q-mb-md">{{ t('stats.freq_mod_emissions.title') }}</div>
          <div>{{ stats.emissions.freq_mod }}</div>
        </div>
      </div>
      <div class="row q-col-gutter-md">
        <div class="col">
          <div class="text-h6 q-mt-md q-mb-md">{{ t('stats.mod_reco.title') }}</div>
          <div>{{ stats.links.mod_reco }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import FrequenciesChart from 'src/components/charts/FrequenciesChart.vue'
import ShareChart from 'src/components/charts/ShareChart.vue'
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
