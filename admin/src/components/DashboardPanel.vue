<template>
  <div>
    <div class="row q-mb-md">
      <q-select
        dense
        multiple
        emit-value
        map-options
        use-chips
        rounded
        outlined
        color="field"
        bg-color="field"
        v-model="companyFilter"
        :label="t('companies')"
        :options="companyOptions"
        style="min-width: 200px"
        @update:model-value="onFilter"
        class="on-left"
      >
        <template v-slot:option="{ itemProps, opt, selected }">
          <q-item v-bind="itemProps">
            <q-item-section>
              <q-item-label>{{ opt.label }}</q-item-label>
            </q-item-section>
            <q-item-section side>
              <q-icon v-if="selected" name="check" />
            </q-item-section>
          </q-item>
        </template>
      </q-select>
      <q-select
        dense
        multiple
        emit-value
        map-options
        use-chips
        rounded
        outlined
        color="field"
        bg-color="field"
        v-model="campaignFilter"
        :label="t('campaigns')"
        :options="campaignOptions"
        style="min-width: 200px"
        @update:model-value="onFilter"
        class="on-left"
      />
      <q-btn size="sm" color="field" outline no-caps>
        {{ t('stats.options') }} <q-icon name="arrow_drop_down" />
        <q-menu>
          <q-list style="min-width: 150px">
            <q-item clickable v-close-popup @click="onMapFilter">
              <q-item-section icon="map">{{ t('stats.filter_by_zone') }}</q-item-section>
              <q-item-section side>
                <q-badge v-if="areaCount > 0" color="orange" />
              </q-item-section>
            </q-item>
            <q-item clickable v-close-popup @click="goToReport" :disable="stats.loading">
              <q-item-section icon="picture_as_pdf">{{ t('stats.pdf_report') }}</q-item-section>
            </q-item>
            <q-separator />
            <q-item class="q-mr-sm">
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

      <download-data-button
        :company-filter="companyFilter"
        :campaign-filter="campaignFilter"
        class="on-right"
      />
    </div>
    <div v-if="stats.loading">
      <div class="spinner-container">
        <q-spinner-dots size="64px" color="primary" />
      </div>
    </div>
    <div v-else>
      <charts-panel :height="height" :collaborators-count="totalCollaboratorsCount" />
    </div>
    <area-dialog
      v-model="showMapFilter"
      :title="t('map_filter.workplaces.title')"
      :text="t('map_filter.workplaces.hint')"
      @select="onWorkplacesFilter"
    />
  </div>
</template>

<script setup lang="ts">
import ChartsPanel from 'src/components/charts/ChartsPanel.vue'
import AreaDialog from 'src/components/AreaDialog.vue'
import DownloadDataButton from 'src/components/DownloadDataButton.vue'
import type { Company, Campaign } from 'src/models'
import type { Filter } from 'src/components/models'
import { useQuasar } from 'quasar'
import MarkdownDialog from 'src/components/MarkdownDialog.vue'

const { t } = useI18n()
const stats = useStats()
const services = useServices()
const companyService = services.make('company')
const campaignService = services.make('campaign')
const $q = useQuasar()

const height = ref(400)
const companyMap = ref<{ [key: string]: Company }>({})
const campaignMap = ref<{ [key: string]: Campaign }>({})
const showMapFilter = ref(false)

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

const selectedCampaigns = computed(() => {
  const allCampaigns = Object.values(campaignMap.value)
  const filteredByCompanies = companyFilter.value.length
    ? allCampaigns.filter((campaign) => companyFilter.value.includes(`${campaign.company_id}`))
    : allCampaigns
  const filteredByCampaigns = campaignFilter.value.length
    ? filteredByCompanies.filter((campaign) => campaignFilter.value.includes(`${campaign.id}`))
    : filteredByCompanies
  return filteredByCampaigns
})

const totalCollaboratorsCount = computed(() => {
  return selectedCampaigns.value.reduce(
    (sum, campaign) => sum + (campaignMap.value[`${campaign.id}`]?.nb_employees || 0),
    0,
  )
})

const areaFilter = ref<GeoJSON.FeatureCollection | undefined>(undefined)
const areaCount = computed(() => {
  if (areaFilter.value && areaFilter.value.features.length > 0) {
    return areaFilter.value.features.length
  }
  return 0
})

onMounted(() => {
  stats.loadStats()
  companyService.find({ $limit: 1000, $select: ['id', 'name'] }).then((result) => {
    const companies = result.data
    companies.forEach((company: Company) => {
      companyMap.value[`${company.id}`] = company
    })
  })
  campaignService
    .find({ $limit: 1000, $select: ['id', 'name', 'company_id', 'nb_employees'] })
    .then((result) => {
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
  if (areaFilter.value) {
    query.workplace_location = {
      $geoWithin: {
        $geometry: areaFilter.value.features[0]?.geometry,
      },
    }
  }
  stats.loadStats(query)
}

function onMapFilter() {
  showMapFilter.value = true
}

function onWorkplacesFilter(area: GeoJSON.FeatureCollection | undefined) {
  areaFilter.value = area
  onFilter()
}

async function goToReport() {
  $q.dialog({
    component: MarkdownDialog,
    componentProps: {
      text: t('report_data_protection_notice.content'),
      title: t('report_data_protection_notice.title'),
      canCancel: true,
    },
    persistent: true,
  }).onOk(() => {
    openReport()
  })
}

async function openReport() {
  const id = stats.dumpToLocalStorage()

  const url = new URL(window.location.href)
  url.pathname = '/admin/report'

  let displayedOrgs =
    companyFilter.value.length > 0 ? companyFilter.value : Object.keys(companyMap.value)

  let displayedCampaigns = campaignFilter.value
  if (campaignFilter.value.length === 0) {
    const campaignsInDisplayedOrgs = Object.values(campaignMap.value).filter(
      (campaign) => displayedOrgs.some((orgId) => orgId == `${campaign.company_id}`), // use loose equality to compare string and number IDs
    )
    displayedCampaigns = campaignsInDisplayedOrgs.map((campaign) => `${campaign.id}`)
  } else {
    // If we filtered by campaigns, make sure we remove the orgs that are not in the filtered campaigns from the report filters
    displayedOrgs = displayedOrgs.filter((orgId) =>
      campaignFilter.value.some(
        (campaignId) => `${campaignMap.value[campaignId]?.company_id}` === orgId,
      ),
    )
  }

  url.searchParams.set(
    'orgs',
    displayedOrgs.map((id) => companyMap.value[`${id}`]?.name || id).join(';'),
  )
  url.searchParams.set(
    'campaigns',
    displayedCampaigns.map((id) => campaignMap.value[`${id}`]?.name || id).join(';'),
  )

  url.searchParams.set('statsStateId', id)

  url.searchParams.set('freqModalType', stats.freqModalType)
  url.searchParams.set('emModalType', stats.emModalType)
  url.searchParams.set('redModalType', stats.redModalType)
  url.searchParams.set('redShareModalType', stats.redShareModalType)

  url.searchParams.set('travelTimePercent', String(stats.travelTimePercent))
  url.searchParams.set('equipmentsPercent', String(stats.equipmentsPercent))
  url.searchParams.set('constraintsPercent', String(stats.constraintsPercent))
  url.searchParams.set('freqModProPercent', String(stats.freqModProPercent))
  url.searchParams.set('leversPercent', String(stats.leversPercent))
  url.searchParams.set('motivationPercent', String(stats.motivationPercent))

  window.open(url.toString(), '_blank')
}
</script>

<style scoped>
.spinner-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}
</style>
