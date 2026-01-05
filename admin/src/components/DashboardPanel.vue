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
      <q-btn size="sm" flat icon="map" @click="onMapFilter">
        <q-badge v-if="areaCount > 0" color="orange" floating rounded />
      </q-btn>
      <q-btn
        size="sm"
        flat
        :icon="layout === 'grid' ? 'slideshow' : 'grid_view'"
        @click="layout = layout === 'grid' ? 'carousel' : 'grid'"
      />
      <q-btn
        size="sm"
        flat
        icon="picture_as_pdf"
        @click="onPDFExport"
        :loading="exportingPDF"
        :disable="layout === 'carousel'"
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
import html2canvas from 'html2canvas'
import ChartsPanel from 'src/components/charts/ChartsPanel.vue'
import ChartsCarousel from 'src/components/charts/ChartsCarousel.vue'
import AreaDialog from 'src/components/AreaDialog.vue'
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
  exportingPDF.value = true
  try {
    // Temporarily switch to grid view to capture all charts
    const originalLayout = layout.value
    if (layout.value === 'carousel') {
      layout.value = 'grid'
      // Wait for the DOM to update
      await nextTick()
      // Wait a bit more for charts to render
      await new Promise((resolve) => setTimeout(resolve, 500))
    }

    const doc = new jsPDF({ orientation: 'landscape' })

    const pageWidth = doc.internal.pageSize.getWidth()
    const pageHeight = doc.internal.pageSize.getHeight()
    const margin = 10
    const maxWidth = pageWidth - 2 * margin
    const maxHeight = pageHeight - 2 * margin
    let topMargin = 15

    // Add title
    doc.setFontSize(36)
    doc.setTextColor(1, 152, 59) // Primary color #01983b
    doc.text(t('stats.title'), margin, topMargin)
    topMargin += 7
    doc.setTextColor(0, 0, 0) // Reset to black
    doc.setFontSize(10)
    doc.text(new Date().toLocaleString(), margin, topMargin)
    // Add filter selections
    let filterText = ''
    if (companyFilter.value.length > 0) {
      const companyNames = companyFilter.value
        .map((id) => companyOptions.value.find((c) => `${c.value}` === `${id}`)?.label || id)
        .join(', ')
      filterText += `${t('companies')}: ${companyNames}`
    }
    if (filterText) {
      topMargin += 7
      doc.text(filterText, margin, topMargin)
    }
    filterText = ''
    if (campaignFilter.value.length > 0) {
      const campaignNames = campaignFilter.value
        .map((id) => campaignOptions.value.find((c) => `${c.value}` === `${id}`)?.label || id)
        .join(', ')
      filterText += `${t('campaigns')}: ${campaignNames}`
    }
    if (filterText) {
      topMargin += 7
      doc.text(filterText, margin, topMargin)
    }

    // Get all chart containers
    const chartContainers = document.querySelectorAll('.item')

    if (chartContainers.length === 0) {
      doc.setFontSize(12)
      doc.text(t('stats.no_charts_to_export'), margin, 40)
      doc.save(`report_${new Date().toISOString()}.pdf`)
      layout.value = originalLayout
      return
    }

    let capturedCount = 0

    for (let i = 0; i < chartContainers.length; i++) {
      const container = chartContainers[i] as HTMLElement

      // Skip if container is not visible or has no dimensions
      if (container.offsetWidth === 0 || container.offsetHeight === 0) {
        continue
      }

      try {
        const canvas = await html2canvas(container, {
          scale: 2,
          logging: false,
          useCORS: true,
          backgroundColor: '#ffffff',
        })

        const imgData = canvas.toDataURL('image/png')
        const imgWidth = canvas.width
        const imgHeight = canvas.height
        const ratio = imgWidth / imgHeight

        // Calculate dimensions to fit the page
        let finalWidth = maxWidth
        let finalHeight = finalWidth / ratio

        if (finalHeight > maxHeight) {
          finalHeight = maxHeight
          finalWidth = finalHeight * ratio
        }

        // Add new page for each chart except the first
        doc.addPage()

        // Center the image on the page
        const x = (pageWidth - finalWidth) / 2
        const y = (pageHeight - finalHeight) / 2

        doc.addImage(imgData, 'PNG', x, y, finalWidth, finalHeight)
        capturedCount++
      } catch (error) {
        console.error('Error capturing chart:', error)
      }
    }

    if (capturedCount > 0) {
      doc.save(`report_${new Date().toISOString()}.pdf`)
    }

    // Restore original layout
    layout.value = originalLayout
  } catch (error) {
    console.error('Error generating PDF:', error)
  } finally {
    exportingPDF.value = false
  }
}
</script>
