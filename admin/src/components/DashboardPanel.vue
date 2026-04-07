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
      <q-btn-group unelevated outline class="bg-field">
        <q-btn
          class="right-border"
          size="sm"
          icon="map"
          color="field"
          outline
          dense
          :label="t('stats.filter_by_zone')"
          no-caps
          @click="onMapFilter"
        >
          <q-badge v-if="areaCount > 0" color="orange" floating rounded />
        </q-btn>
        <q-btn
          class="right-border"
          size="sm"
          color="field"
          outline
          dense
          :icon="layout === 'grid' ? 'slideshow' : 'grid_view'"
          :label="layout === 'grid' ? t('stats.switch_to_carousel') : t('stats.switch_to_grid')"
          no-caps
          @click="layout = layout === 'grid' ? 'carousel' : 'grid'"
        />
        <q-btn
          class="right-border"
          size="sm"
          color="field"
          outline
          dense
          icon="picture_as_pdf"
          :loading="exportingPDF"
          :disable="stats.loading || exportingPDF"
          :label="t('stats.pdf_report')"
          no-caps
          @click="onPDFExport"
        />
        <q-btn icon="settings" size="sm" color="field" outline>
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
      </q-btn-group>
    </div>
    <div v-if="stats.loading">
      <div class="spinner-container">
        <q-spinner-dots size="64px" color="primary" />
      </div>
    </div>
    <div v-else-if="layout === 'grid'">
      <charts-panel :percent="percent" :height="height" />
    </div>
    <div v-else>
      <charts-carousel :percent="percent" :height="height" />
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
import { jsPDF } from 'jspdf'
import ChartsPanel from 'src/components/charts/ChartsPanel.vue'
import ChartsCarousel from 'src/components/charts/ChartsCarousel.vue'
import AreaDialog from 'src/components/AreaDialog.vue'
import type { Company, Campaign } from 'src/models'
import type { Filter } from 'src/components/models'
import { notifyError } from 'src/utils/notify'
import { makeChartPage } from 'src/utils/report'

const { t } = useI18n()
const stats = useStats()
const services = useServices()
const companyService = services.make('company')
const campaignService = services.make('campaign')

const layout = ref('grid')
const percent = ref(true)
const height = ref(400)
const exportingPDF = ref(false)
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

async function onPDFExport() {
  // Add filter selections
  const filters = []
  if (companyFilter.value.length > 0) {
    let filterText = ''
    const companyNames = companyFilter.value
      .map((id) => companyOptions.value.find((c) => `${c.value}` === `${id}`)?.label || id)
      .join(', ')
    filterText += `${t('companies')}: ${companyNames}`
    if (filterText) {
      filters.push(filterText)
    }
  }
  if (campaignFilter.value.length > 0) {
    let filterText = ''
    const campaignNames = campaignFilter.value
      .map((id) => campaignOptions.value.find((c) => `${c.value}` === `${id}`)?.label || id)
      .join(', ')
    filterText += `${t('campaigns')}: ${campaignNames}`
    if (filterText) {
      filters.push(filterText)
    }
  }

  const doc = new jsPDF({ orientation: 'landscape' })
  const pageWidth = doc.internal.pageSize.getWidth()
  const pageHeight = doc.internal.pageSize.getHeight()
  const margin = 10
  const now = new Date()

  exportingPDF.value = true
  try {
    // Get all carousel slides
    const chartContainers = document.querySelectorAll('.echarts')
    if (chartContainers.length === 0) {
      notifyError(t('stats.no_charts_to_export'))
      return
    }

    if (layout.value === 'grid') {
      // Grid layout export
      let topMargin = 25

      // Add title
      doc.setFontSize(54)
      doc.setTextColor(1, 152, 59) // Primary color #01983b
      doc.text(t('main.brand'), pageWidth / 2, topMargin, { align: 'center' })
      topMargin += 14
      doc.setFontSize(24)
      doc.setTextColor(0, 0, 0) // Reset to black
      doc.text(t('stats.title'), pageWidth / 2, topMargin, { align: 'center' })
      topMargin = pageHeight - 15
      doc.setFontSize(10)
      doc.text(now.toLocaleString(), margin, topMargin)

      if (filters.length > 0) {
        doc.text(filters.join(' | '), pageWidth - margin, topMargin, { align: 'right' })
      }
      // Move to next page
      doc.addPage()
    }
    let capturedCount = 0
    for (let i = 0; i < chartContainers.length; i++) {
      const chart = chartContainers[i] as HTMLElement
      const chartId = chart.getAttribute('data-chart-id')
      const text = document.querySelector<HTMLElement>(`.chart-text[data-chart-id="${chartId}"]`)

      // Skip if chart is not visible or has no dimensions
      if (chart.offsetWidth === 0 || chart.offsetHeight === 0) {
        continue
      }

      const added = await makeChartPage(
        chart,
        text?.innerText,
        doc,
        now,
        t('main.brand'),
        `${t('stats.title')}`,
        filters.join(' | '),
      )
      if (added) {
        capturedCount++
        if (i < chartContainers.length - 1) {
          doc.addPage()
        }
      }
    }

    if (capturedCount > 0) {
      doc.save(
        `${t('main.brand').replaceAll(' ', '_')}_${t('stats.title').replaceAll(' ', '_')}_${new Date().toISOString()}.pdf`,
      )
    } else {
      notifyError(t('stats.no_charts_to_export'))
    }
  } catch (error) {
    console.error('Error generating PDF:', error)
    notifyError(t('error.pdf_export_failed'))
  } finally {
    exportingPDF.value = false
  }
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
