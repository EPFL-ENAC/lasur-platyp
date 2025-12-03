<template>
  <div>
    <div class="row q-mb-md">
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
        class="on-left"
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
        class="on-left"
      />
      <q-btn
        size="sm"
        flat
        :icon="layout === 'grid' ? 'slideshow' : 'grid_view'"
        @click="layout = layout === 'grid' ? 'carousel' : 'grid'"
      />
      <q-btn flat color="primary" icon="settings" size="sm">
        <q-menu>
          <q-list style="min-width: 100px">
            <q-item>
              <q-checkbox v-model="percent" :label="t('stats.percent_employees')" />
            </q-item>
            <q-item class="q-mb-md q-mr-sm">
              <div style="width: 200px">
                <div>{{ t('stats.charts_height') }}</div>
                <q-slider
                  v-model="height"
                  :min="200"
                  :max="600"
                  :step="50"
                  label
                  switch-label-side
                  style="max-width: 200px"
                />
              </div>
            </q-item>
          </q-list>
        </q-menu>
      </q-btn>
    </div>
    <div v-if="stats.loading">
      <q-spinner-dots size="md" color="primary" />
    </div>
    <div v-else-if="layout === 'grid'">
      <charts-panel :percent="percent" :height="height" />
    </div>
    <div v-else>
      <charts-carousel :percent="percent" :height="height" />
    </div>
  </div>
</template>

<script setup lang="ts">
import ChartsPanel from 'src/components/charts/ChartsPanel.vue'
import ChartsCarousel from 'src/components/charts/ChartsCarousel.vue'
import type { Company, Campaign } from 'src/models'
import type { Filter } from 'src/components/models'

const { t } = useI18n()
const stats = useStats()
const services = useServices()
const companyService = services.make('company')
const campaignService = services.make('campaign')

const layout = ref('grid')
const percent = ref(true)
const height = ref(400)
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
