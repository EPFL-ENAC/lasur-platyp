<template>
  <div :style="`height: ${height}px; width: 100%;`">
    <e-charts
      v-if="total > 0"
      ref="chart"
      autoresize
      :init-options="initOptions"
      :option="option"
      :update-options="updateOptions"
      :loading="stats.loading"
      :theme="$q.dark.isActive ? 'platyp-dark' : 'platyp'"
      :data-chart-id="chartId"
    />
    <div v-else>
      <div class="text-h6 text-center">{{ t(`stats.energy_journey.title_share`) }}</div>
      <div class="text-subtitle1 text-foreground text-center">{{ t('stats.no_data') }}</div>
    </div>
  </div>

  <div class="q-mt-md chart-text" :data-chart-id="chartId">
    <p class="q-mb-xs">{{ t(`stats.energy_journey.texts.default_share`) }}</p>
    <q-markdown
      v-if="total > 5 && biggestShare"
      :src="
        t(`stats.energy_journey.texts.specific_share`, {
          percentage: formatNumber(biggestShare.percentage),
          mode: keyLabel(biggestShare.mode),
        })
      "
    />
  </div>
</template>

<script setup lang="ts">
import ECharts from 'vue-echarts'
import type { EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import { initOptions, MODE_COLORS, updateOptions } from './commons'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import { formatNumber } from 'src/utils/numbers'
import type { CallbackDataParams } from 'echarts/types/dist/shared'
import { useQuasar } from 'quasar'
import { getRandomId } from 'src/utils/random'
// import { MODE_COLORS } from './commons'

const { t, locale } = useI18n()
const $q = useQuasar()
const stats = useStats()
use([SVGRenderer, PieChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  height?: number
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

interface AddedEnergyShare {
  mode: string
  percentage: number
}

const chartId = getRandomId()
const option = ref<EChartsOption>({})
const total = ref(0)
const biggestShare = ref<AddedEnergyShare | null>(null)

watch([() => stats.loading], () => {
  if (stats.loading) {
    initChartOptions()
  }
})

watch([() => props.height, locale], () => {
  if (!stats.loading) {
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
  return t(`stats.energy_journey.labels.${shortKey(key)}`)
}

function initChartOptions() {
  option.value = {}
  total.value = 0

  const rawData = stats.journeyEnergyStats.gains?.gains_per_mode || []

  if (rawData.length === 0) return

  const filtered = rawData.filter((item) => item.added_kcal > 0)
  total.value = filtered.length

  const sumPositiveEnergy = filtered.reduce((sum, item) => sum + item.added_kcal, 0)

  biggestShare.value = {
    mode: '',
    percentage: 0,
  }
  filtered.forEach((item) => {
    const percentage = sumPositiveEnergy > 0 ? (item.added_kcal / sumPositiveEnergy) * 100 : 0
    if (!biggestShare.value || percentage > biggestShare.value.percentage) {
      biggestShare.value = { mode: item.mode, percentage }
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
      text: t(`stats.energy_journey.title_share`),
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

        return `${p.name}<br/><b>${formatNumber(p.value as number)} kcal</b> (${p.percent}%)`
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
        radius: '70%',
        top: 'middle',
        avoidLabelOverlap: true,
        label: {
          show: true,
          position: 'outer',
          formatter: function (params) {
            if (params.value === 0) {
              return ''
            }
            return formatNumber(params.value as number)
          },
        },
        data: filtered.map((item) => ({
          name: keyLabel(item.mode),
          value: item.added_kcal,
        })),
        color: filtered.map((item) => MODE_COLORS[item.mode] || '#FCC447'),
      },
    ],
  }
  option.value = newOption
}

function shortKey(key: string) {
  return key.replace('freq_mod_pro_', '').replace('freq_mod_', '')
}
</script>
