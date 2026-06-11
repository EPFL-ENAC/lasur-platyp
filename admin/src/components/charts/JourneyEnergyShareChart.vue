<template>
  <e-charts-shell
    :height="height"
    :loading="props.loading"
    :has-data="total > 0"
    :show-info="total > 0"
    :no-data-title="t('stats.energy_journey.title_share')"
    :option="option"
    :exportable="!!exportable"
  >
    <p class="q-mb-xs">{{ t('stats.energy_journey.texts.default_share') }}</p>
    <q-markdown
      v-if="total > 5 && biggestShare"
      :src="
        t('stats.energy_journey.texts.specific_share', {
          percentage: formatNumber(biggestShare.percentage),
          mode: keyLabel(biggestShare.mode),
        })
      "
    />
  </e-charts-shell>
</template>

<script setup lang="ts">
import EChartsShell from './EChartsShell.vue'
import type { EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import { MODE_COLORS, MODE_IDEAL_ORDER } from './commons'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import { formatNumber } from 'src/utils/numbers'
import type { CallbackDataParams } from 'echarts/types/dist/shared'
import type { JourneyEnergyStats } from 'src/models'

const { t, locale } = useI18n()
use([SVGRenderer, PieChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  journeyEnergyStats?: JourneyEnergyStats | null
  height?: number
  loading?: boolean
  exportable?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
  exportable: true,
})

interface AddedEnergyShare {
  mode: string
  percentage: number
}

const option = ref<EChartsOption>({})
const total = ref(0)
const biggestShare = ref<AddedEnergyShare | null>(null)

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

function keyLabel(key: string) {
  if (key === 'null' || key === 'None') {
    return 'N/A'
  }
  // is integer ?
  if (Number.isInteger(Number(key))) {
    return key
  }
  return t(`transportation_modes.${shortKey(key)}`)
}

function initChartOptions() {
  option.value = {}
  total.value = 0

  const rawData = props.journeyEnergyStats?.gains?.gains_per_mode || []

  if (rawData.length === 0) return

  const filtered = rawData.filter((item) => item.added_kcal > 0)
  filtered.sort((a, b) => (MODE_IDEAL_ORDER[a.mode] ?? 0) - (MODE_IDEAL_ORDER[b.mode] ?? 0))
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
