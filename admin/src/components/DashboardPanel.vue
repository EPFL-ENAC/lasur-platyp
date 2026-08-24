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
        :disable="stats.loading"
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
        v-model="mainGroupFilter"
        :label="t('stats.main_group')"
        :options="campaignOptions"
        style="min-width: 200px"
        @update:model-value="onFilter"
        :disable="stats.loading"
        class="on-left"
      />
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
        v-model="compareWithFilter"
        :label="t('stats.compare_with')"
        :options="compareWithOptions"
        style="min-width: 200px"
        @update:model-value="onFilter"
        class="on-left"
        :disable="stats.loading"
      />
      <div
        v-for="(group, index) in additionalCompareGroups"
        :key="index"
        class="row items-center on-left"
      >
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
          v-model="additionalCompareGroups[index]"
          :label="`${t('stats.also_compare_with')} ${index + 1}`"
          :options="additionalGroupOptions(index)"
          style="min-width: 200px"
          @update:model-value="onFilter"
          :disable="stats.loading"
        />
        <q-btn
          flat
          round
          dense
          size="sm"
          icon="close"
          :aria-label="t('remove')"
          @click="removeAdditionalGroup(index)"
          :disable="stats.loading"
        />
      </div>
      <q-btn
        flat
        dense
        no-caps
        color="field"
        icon="add"
        :label="t('stats.add_more_comparisons')"
        :disable="!canAddMoreComparisons || stats.loading"
        @click="addComparisonGroup"
        class="on-left"
      />
      <q-btn size="sm" color="field" outline no-caps :disable="stats.loading">
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
        :campaign-filter="mainGroupFilter"
        class="on-right"
      />
    </div>
    <div v-if="hasComparisonGroups" class="row items-center q-mb-md">
      <q-btn-toggle
        v-model="comparisonModeToggle"
        no-caps
        dense
        rounded
        unelevated
        toggle-color="primary"
        color="white"
        text-color="primary"
        :options="[
          { label: t('stats.cross_sectional'), value: 'cross_sectional' },
          { label: t('stats.longitudinal'), value: 'longitudinal' },
        ]"
        @update:model-value="onFilter"
        :disable="stats.loading"
      />
    </div>
    <div v-if="!stats.loading && hasComparisonGroups" class="q-mb-md" >
      <q-separator class="q-mb-md" />
      <div>
        <q-chip v-for="(group, idx) in stats.comparisonResults?.groups" :key="group.name" class="text-white" :style="{ backgroundColor: GROUP_COLORS[idx % GROUP_COLORS.length] }">
          {{ t('stats.group_info', { name: group.name, count: group.total }) }}
        </q-chip>
      </div>
    </div>
    <q-banner
      v-if="stats.privacyWarnings.length > 0"
      dense
      rounded
      class="bg-warning text-white q-mb-md"
    >
      {{ t('stats.too_few_records', { groups: `"${stats.privacyWarnings.join('", "')}"` }) }}
    </q-banner>
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
import type { Company, Campaign, CampaignGroup, ComparisonMode } from 'src/models'
import type { Filter } from 'src/components/models'
import { useQuasar } from 'quasar'
import MarkdownDialog from 'src/components/MarkdownDialog.vue'
import { GROUP_COLORS } from 'src/components/charts/commons'

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

const companyFilter = ref<number[]>([])
const companyOptions = computed(() => {
  return Object.values(companyMap.value)
    .map((company) => ({
      label: company.name,
      value: company.id,
    }))
    .sort((a, b) => a.label.localeCompare(b.label))
})

const mainGroupFilter = ref<number[]>([])
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
    ? allCampaigns.filter((campaign) => companyFilter.value.includes(campaign.company_id))
    : allCampaigns
  const filteredByCampaigns = mainGroupFilter.value.length
    ? filteredByCompanies.filter((campaign) => mainGroupFilter.value.includes(campaign.id))
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

// "Main Group" resolved to concrete campaign ids: explicit selection, or every
// campaign currently in scope (company filter applied) when left empty.
const mainGroupCampaignIds = computed<number[]>(() => {
  return mainGroupFilter.value.length > 0
    ? mainGroupFilter.value.map((id) => Number(id))
    : selectedCampaigns.value.map((campaign) => campaign.id as number)
})

function optionsExcluding(excludeIds: (string | number)[]) {
  const excludeSet = new Set(excludeIds.map((id) => `${id}`))
  return campaignOptions.value.filter((option) => !excludeSet.has(`${option.value}`))
}

const compareWithFilter = ref<string[]>([])
const compareWithOptions = computed(() => optionsExcluding(mainGroupCampaignIds.value))

// Extra "Also compare with" rows, each a list of campaign ids for one more group.
const additionalCompareGroups = ref<string[][]>([])

function additionalGroupOptions(index: number) {
  const excluded = [
    ...mainGroupCampaignIds.value,
    ...compareWithFilter.value,
    ...additionalCompareGroups.value.flatMap((ids, i) => (i === index ? [] : ids)),
  ]
  return optionsExcluding(excluded)
}

// Main Group + up to 4 "compare with" groups, matching the comparison chart palette size.
const MAX_COMPARISON_GROUPS = 5
// The fixed "Compare with" row plus however many "Also compare with" rows were added.
const MAX_COMPARE_WITH_ROWS = MAX_COMPARISON_GROUPS - 1
const canAddMoreComparisons = computed(
  () => 1 + additionalCompareGroups.value.length < MAX_COMPARE_WITH_ROWS,
)

const hasComparisonGroups = computed(
  () =>
    compareWithFilter.value.length > 0 ||
    additionalCompareGroups.value.some((ids) => ids.length > 0),
)

const comparisonModeToggle = ref<ComparisonMode>('cross_sectional')

function addComparisonGroup() {
  additionalCompareGroups.value.push([])
}

function removeAdditionalGroup(index: number) {
  const hadSelection = (additionalCompareGroups.value[index]?.length ?? 0) > 0
  additionalCompareGroups.value.splice(index, 1)
  if (hadSelection) {
    onFilter()
  }
}

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

function buildBaseFilter(): Filter {
  const query = {} as Filter
  if (companyFilter.value.length > 0) {
    query.company_id = { $in: companyFilter.value }
  }
  if (areaFilter.value) {
    query.workplace_location = {
      $geoWithin: {
        $geometry: areaFilter.value.features[0]?.geometry,
      },
    }
  }
  return query
}

function buildComparisonGroups(): CampaignGroup[] {
  const groups: CampaignGroup[] = [
    { name: t('stats.main_group'), campaign_ids: mainGroupCampaignIds.value },
  ]
  if (compareWithFilter.value.length > 0) {
    groups.push({
      name: t('stats.compare_with'),
      campaign_ids: compareWithFilter.value.map((id) => Number(id)),
    })
  }
  additionalCompareGroups.value.forEach((ids, index) => {
    if (ids.length > 0) {
      groups.push({
        name: `${t('stats.also_compare_with')} ${index + 1}`,
        campaign_ids: ids.map((id) => Number(id)),
      })
    }
  })
  return groups
}

function onFilter() {
  if (hasComparisonGroups.value) {
    stats.loadComparison(buildComparisonGroups(), comparisonModeToggle.value, buildBaseFilter())
    return
  }

  const query = buildBaseFilter()
  if (mainGroupFilter.value.length > 0) {
    query.campaign_id = { $in: mainGroupFilter.value }
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
  const id = await stats.dumpToIndexedDB()

  const url = new URL(window.location.href)
  url.pathname = '/admin/report'

  // In comparison mode, the report should reflect every campaign across all groups,
  // not just the Main Group.
  const reportCampaignFilter = hasComparisonGroups.value
    ? [
        ...new Set([
          ...mainGroupFilter.value,
          ...compareWithFilter.value,
          ...additionalCompareGroups.value.flat(),
        ]),
      ]
    : mainGroupFilter.value

  let displayedOrgs =
    companyFilter.value.length > 0 ? companyFilter.value : Object.keys(companyMap.value)

  let displayedCampaigns = reportCampaignFilter
  if (reportCampaignFilter.length === 0) {
    const campaignsInDisplayedOrgs = Object.values(campaignMap.value).filter(
      (campaign) => displayedOrgs.some((orgId) => orgId == `${campaign.company_id}`), // use loose equality to compare string and number IDs
    )
    displayedCampaigns = campaignsInDisplayedOrgs.map((campaign) => `${campaign.id}`)
  } else {
    // If we filtered by campaigns, make sure we remove the orgs that are not in the filtered campaigns from the report filters
    displayedOrgs = displayedOrgs.filter((orgId) =>
      reportCampaignFilter.some(
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
