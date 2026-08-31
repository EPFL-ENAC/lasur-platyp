<template>
  <chart-panel
    :title="chartTitle"
    :description="t('stats.energy_journey.description_share')"
    :chart-info-text="chartDescription"
    :inline="inline"
  >
    <q-toolbar v-if="!inline" class="chart-toolbar">
      <q-space />
      <q-btn flat icon="more_vert">
        <q-menu>
          <q-list style="min-width: 200px">
            <q-item clickable v-close-popup @click="onToggleModalType">
              <q-item-section side>
                <q-icon :name="modalType === 'simple' ? 'pie_chart' : 'lens'" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{
                  modalType === 'simple'
                    ? t('stats.freq_mod.modal_split.detailed')
                    : t('stats.freq_mod.modal_split.simple')
                }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item clickable v-close-popup @click="onChartDownload">
              <q-item-section side>
                <q-icon name="download" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ t('download') }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-menu>
      </q-btn>
    </q-toolbar>
    <e-charts-shell
      ref="shellRef"
      :height="height"
      :loading="props.loading"
      :has-data="total > 0"
      :show-table="!exportable"
      :no-data-title="chartTitle"
      :option="option"
      :exportable="!!exportable"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from '@/components/charts/ChartPanel.vue'
import EChartsShell from './EChartsShell.vue'
import type { EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import { MODE_COLORS, SIMPLE_LABELS_COLORS, modeSortOrder, simpleLabelSortOrder } from './commons'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import { formatNumber } from '@/utils/numbers'
import type { CallbackDataParams } from 'echarts/types/dist/shared'
import type { JourneyEnergyStats } from '@/models'

const { t, locale } = useI18n()
use([SVGRenderer, PieChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  journeyEnergyStats?: JourneyEnergyStats | null
  height?: number
  loading?: boolean
  exportable?: boolean
  inline?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
  exportable: true,
})

interface AddedEnergyShare {
  label: string
  percentage: number
}

type EChartsShellExposed = {
  handleExport: () => Promise<void>
}

const shellRef = useTemplateRef<EChartsShellExposed>('shellRef')

const modalType = ref<'simple' | 'detailed'>('simple')

function onToggleModalType() {
  modalType.value = modalType.value === 'simple' ? 'detailed' : 'simple'
  initChartOptions()
}

function keyLabel(key: string) {
  if (key === 'null' || key === 'None') {
    return 'N/A'
  }
  if (Number.isInteger(Number(key))) {
    return key
  }
  const namespace = modalType.value === 'simple' ? 'simple_labels' : 'transportation_modes'
  return t(`${namespace}.${shortKey(key)}`)
}

function onChartDownload() {
  shellRef.value?.handleExport()
}

const chartTitle = computed(
  () =>
    `${t('stats.energy_journey.title_share')} (${t(`stats.freq_mod.modal_split.${modalType.value}`).toLowerCase()})`,
)

const option = ref<EChartsOption>({})
const total = ref(0)
const biggestShare = ref<AddedEnergyShare | null>(null)

const chartDescription = computed(() => {
  if (total.value > 5 && biggestShare.value) {
    return t('stats.energy_journey.texts.specific_share', {
      percentage: formatNumber(biggestShare.value.percentage),
      mode: keyLabel(biggestShare.value.label),
    })
  }
  return ''
})

defineExpose({
  handleExport: () => shellRef.value?.handleExport(),
  get chartInfoText() {
    return chartDescription.value
  },
})

watch([() => props.loading], () => {
  if (props.loading) {
    initChartOptions()
  }
})

watch([() => props.height, locale], () => {
  if (!props.loading) {
    initChartOptions()
  }
})

onMounted(() => {
  initChartOptions()
})

function initChartOptions() {
  option.value = {}
  total.value = 0

  const rawData = props.journeyEnergyStats?.gains?.gains_per_mode[modalType.value] || []

  if (rawData.length === 0) return

  const sortOrder = modalType.value === 'simple' ? simpleLabelSortOrder : modeSortOrder
  const filtered = rawData.filter((item) => item.added_kcal > 0)
  filtered.sort((a, b) => sortOrder(a.label) - sortOrder(b.label))
  total.value = filtered.length

  const sumPositiveEnergy = filtered.reduce((sum, item) => sum + item.added_kcal, 0)

  biggestShare.value = {
    label: '',
    percentage: 0,
  }
  filtered.forEach((item) => {
    const percentage = sumPositiveEnergy > 0 ? (item.added_kcal / sumPositiveEnergy) * 100 : 0
    if (!biggestShare.value || percentage > biggestShare.value.percentage) {
      biggestShare.value = { label: item.label, percentage }
    }
  })

  const newOption: EChartsOption = {
    grid: {
      left: '40',
      right: '20',
      top: '60',
      bottom: '20',
      containLabel: true,
    },
    animation: false,
    height: props.height - 100,
    title: {
      text: chartTitle.value,
      subtext: t(`stats.total`, { count: total.value }),
      left: 'center',
      top: 0,
      itemGap: 10,
      textStyle: {
        fontSize: 16,
      },
    },
    tooltip: {
      trigger: 'item',
      formatter: function (params: CallbackDataParams | CallbackDataParams[]) {
        const p = Array.isArray(params) ? params[0] : params
        if (!p) return ''

        return `${p.name}<br/><b>${p.percent}%</b> (${formatNumber(p.value as number)} kcal)`
      },
    },
    legend: {
      show: true,
      bottom: 16,
      type: 'scroll',
    },
    series: [
      {
        name: 'Added kcal',
        type: 'pie',
        radius: ['40%', '70%'],
        top: 'middle',
        avoidLabelOverlap: true,
        label: {
          show: true,
          position: 'outer',
        },
        data: filtered.map((item) => ({
          name: keyLabel(item.label),
          value: item.added_kcal,
        })),
        color: filtered.map(
          (item) =>
            (modalType.value === 'simple' ? SIMPLE_LABELS_COLORS : MODE_COLORS)[item.label] ||
            '#FCC447',
        ),
      },
    ],
  }
  option.value = newOption
}

function shortKey(key: string) {
  return key.replace('freq_mod_pro_', '').replace('freq_mod_', '')
}
</script>
