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
      <div class="grid-container">
        <div class="item">
          <frequencies-chart
            type="equipments"
            :percent="percent"
            :height="height"
            class="q-mb-md"
          />
        </div>
        <div class="item">
          <frequencies-chart
            type="constraints"
            :percent="percent"
            :height="height"
            class="q-mb-md"
          />
        </div>
        <div class="item">
          <frequencies-chart
            type="travel_time"
            :xaxis="t('stats.travel_time.xaxis')"
            :range-step="5"
            :percent="percent"
            :height="height"
            class="q-mb-md"
          />
        </div>
        <div class="item"><share-chart type="freq_mod" :height="height" class="q-mb-md" /></div>
        <div class="item">
          <frequencies-stack-chart
            type="freq_mod_pro"
            :groups="['local', 'region', 'europe', 'inter']"
            :xaxis="t('stats.freq_mod_pro.xaxis')"
            :height="height"
            class="q-mb-md"
          />
        </div>
        <div class="item">
          <emissions-chart
            type="freq_mod"
            :xaxis="t('stats.emissions_freq_mod.xaxis')"
            :yaxis="t('stats.emissions_freq_mod.yaxis')"
            :height="height"
            class="q-mb-md"
          />
        </div>
        <div class="item">
          <share-chart type="reco_dt2" :height="height" class="q-mb-md" />
        </div>
        <div class="item">
          <links-chart type="mod_reco" :height="height" class="q-mb-md" />
        </div>
      </div>
    </div>
    <div v-else>
      <q-carousel
        v-model="slide"
        :height="`${height + 100}px`"
        transition-prev="scale"
        transition-next="scale"
        control-color="primary"
        navigation
        padding
        arrows
        infinite
      >
        <q-carousel-slide name="equipments" class="column no-wrap flex-center item">
          <frequencies-chart
            type="equipments"
            :percent="percent"
            :height="height"
            class="q-mb-md"
          />
        </q-carousel-slide>
        <q-carousel-slide name="constraints" class="column no-wrap flex-center item">
          <frequencies-chart
            type="constraints"
            :percent="percent"
            :height="height"
            class="q-mb-md"
          />
        </q-carousel-slide>
        <q-carousel-slide name="travel_time" class="column no-wrap flex-center item">
          <frequencies-chart
            type="travel_time"
            :xaxis="t('stats.travel_time.xaxis')"
            :range-step="5"
            :percent="percent"
            :height="height"
            class="q-mb-md"
          />
        </q-carousel-slide>
        <q-carousel-slide name="freq_mod" class="column no-wrap flex-center item">
          <share-chart type="freq_mod" :height="height" class="q-mb-md" />
        </q-carousel-slide>
        <q-carousel-slide name="freq_mod_pro" class="column no-wrap flex-center item">
          <frequencies-stack-chart
            type="freq_mod_pro"
            :groups="['local', 'region', 'inter']"
            :xaxis="t('stats.freq_mod_pro.xaxis')"
            :height="height"
            class="q-mb-md"
          />
        </q-carousel-slide>
        <q-carousel-slide name="emissions_freq_mod" class="column no-wrap flex-center item">
          <emissions-chart
            type="freq_mod"
            :xaxis="t('stats.emissions_freq_mod.xaxis')"
            :yaxis="t('stats.emissions_freq_mod.yaxis')"
            :height="height"
            class="q-mb-md"
          />
        </q-carousel-slide>
        <q-carousel-slide name="reco_dt2" class="column no-wrap flex-center item">
          <share-chart type="reco_dt2" :height="height" class="q-mb-md" />
        </q-carousel-slide>
        <q-carousel-slide name="mod_reco" class="column no-wrap flex-center item">
          <links-chart type="mod_reco" :height="height" class="q-mb-md" />
        </q-carousel-slide>
      </q-carousel>
    </div>
  </div>
</template>

<script setup lang="ts">
import FrequenciesChart from 'src/components/charts/FrequenciesChart.vue'
import FrequenciesStackChart from 'src/components/charts/FrequenciesStackChart.vue'
import EmissionsChart from 'src/components/charts/EmissionsChart.vue'
import LinksChart from 'src/components/charts/LinksChart.vue'
import ShareChart from 'src/components/charts/ShareChart.vue'
import type { Company, Campaign } from 'src/models'
import type { Filter } from 'src/components/models'

const { t } = useI18n()
const stats = useStats()
const services = useServices()
const companyService = services.make('company')
const campaignService = services.make('campaign')

const layout = ref('grid')
const slide = ref('equipments')
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

<style lang="css">
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(600px, 1fr));
  gap: 16px;
}
.item {
  background: #fafafa;
  padding: 16px;
  border: 1px solid #eee;
  border-radius: 4px;
}
</style>
