<template>
  <chart-panel
    :title="t('stats.equipments.title')"
    :description="t('stats.equipments.description')"
    :inline="inline"
  >
    <q-toolbar v-if="!inline" class="chart-toolbar">
      <q-space />
      <q-btn flat icon="more_vert">
        <q-menu>
          <q-list style="min-width: 200px">
            <q-item clickable v-close-popup @click="onTogglePercent">
              <q-item-section side>
                <q-icon :name="stats.equipmentsPercent ? 'check_box' : 'check_box_outline_blank'" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ t('stats.percent_employees') }}</q-item-label>
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
      :has-data="hasData"
      :show-info="stats.equipmentsPercent"
      :show-table="!exportable"
      :no-data-title="t('stats.equipments.title')"
      :option="option"
      :exportable="!!exportable"
    >
      <q-markdown :src="t('stats.equipments.mrmt_source')" />
    </e-charts-shell>
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from 'src/components/charts/ChartPanel.vue'
import EChartsShell from './EChartsShell.vue'
import type { EChartsOption, SeriesOption } from 'echarts'
import { use } from 'echarts/core'
import { BarChart, PictorialBarChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import type { Frequencies } from 'src/models'

const { t, locale } = useI18n()
use([
  SVGRenderer,
  BarChart,
  PictorialBarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
])

interface Props {
  frequencies?: Frequencies | null
  loading?: boolean
  xaxis?: string
  yaxis?: string
  height?: number
  exportable?: boolean
  inline?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
  exportable: true,
})

type EChartsShellExposed = {
  handleExport: () => Promise<void>
}

const shellRef = useTemplateRef<EChartsShellExposed>('shellRef')

function onChartDownload() {
  shellRef.value?.handleExport()
}

const stats = useStats()

function onTogglePercent() {
  stats.equipmentsPercent = !stats.equipmentsPercent
}

const option = ref<EChartsOption>({})
const total = ref(0)

const hasData = computed(() => {
  if (!props.frequencies) {
    return false
  }
  return props.frequencies.data.length > 0
})

watch(
  () => props.loading,
  () => {
    if (props.loading) {
      initChartOptions()
    }
  },
)

watch([() => stats.equipmentsPercent, () => props.height, locale], () => {
  if (!props.loading) {
    initChartOptions()
  }
})

onMounted(() => {
  initChartOptions()
})

function keyLabel(key: string) {
  if (key === 'null' || key === 'None') {
    return 'N/A'
  }
  // is integer ?
  if (Number.isInteger(Number(key))) {
    return key
  }
  return t(`stats.equipments.labels.${key}`)
}

function initChartOptions() {
  option.value = {}
  total.value = 0
  if (!props.frequencies) {
    return
  }

  initLabelsChartOptions(props.frequencies)
}

const MRMT_VALUES_PERCENT = {
  upt_subs: 26,
  car: 71,
  bike: 54,
  train_subs: 19,
  moto: 20,
  ebike: 15,
  mob_subs: 3,
}

function initLabelsChartOptions(frequencies: Frequencies) {
  total.value = frequencies.total || 0

  const dataset = frequencies.data
    .map((item) => ({
      key: item.value || 'null',
      name: keyLabel(item.value || 'null'),
      value: stats.equipmentsPercent
        ? Number(((item.count / total.value) * 100).toFixed(2))
        : item.count,
    }))
    .reverse()

  const categories = dataset.map((item) => item.name)
  const values = dataset.map((item) => item.value)

  const mrmtValues = stats.equipmentsPercent
    ? dataset.map((item) => {
        const mrmt = MRMT_VALUES_PERCENT[item.key as keyof typeof MRMT_VALUES_PERCENT]
        return mrmt ?? null
      })
    : []

  if (categories.length === 0) return

  const maxBarValue = values.length ? Math.max(...values) : 0
  const maxMrmtValue = mrmtValues.filter((v): v is number => v !== null).length
    ? Math.max(...mrmtValues.filter((v): v is number => v !== null))
    : 0
  const xAxisMax = Math.max(maxBarValue, maxMrmtValue)

  const series: SeriesOption[] = [
    {
      name: t('stats.observed'),
      type: 'bar',
      data: values,
    },
  ]
  if (stats.equipmentsPercent) {
    series.push({
      name: t('stats.reference_data'),
      type: 'pictorialBar',
      symbol: 'rect', // This creates the "line" marker
      symbolRepeat: false,
      symbolSize: [4, 32], // [width, height] - height slightly taller than bar
      symbolOffset: [0, 0],
      symbolPosition: 'end',
      itemStyle: {
        color: '#FF5722', // Distinct color for the marker
      },
      data: mrmtValues,
      z: 3, // Ensure it's on top of the bars
    })
  }

  const newOption: EChartsOption = {
    grid: {
      left: '20',
      right: '20',
      top: '60',
      bottom: '60',
      containLabel: true,
    },
    animation: false,
    height: props.height - 100,
    title: {
      text: t(`stats.equipments.title`),
      subtext: t(`stats.total`, { count: total.value }),
      left: 'center',
      top: 0,
      itemGap: 10,
      textStyle: {
        fontSize: 16,
      },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
    },
    legend: {
      show: true,
      bottom: 0,
      data: [t('stats.observed'), t('stats.reference_data')],
    },
    yAxis: {
      name: props.yaxis || '',
      nameLocation: 'end',
      nameGap: 30,
      type: 'category',
      data: categories,
    },
    xAxis: {
      name:
        props.xaxis ||
        (stats.equipmentsPercent ? t('stats.percent_employees') : t('stats.nb_employees')),
      nameLocation: 'middle',
      nameGap: 25,
      type: 'value',
      max: Math.ceil(xAxisMax * 1.1),
    },
    series,
  }

  option.value = newOption
}
</script>
