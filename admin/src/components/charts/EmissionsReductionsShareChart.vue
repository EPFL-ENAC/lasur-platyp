<template>
  <div :style="`height: ${height}px; width: 100%;`">
    <e-charts
      v-if="total > 0"
      ref="chart"
      autoresize
      :init-options="initOptions"
      :option="option"
      :update-options="updateOptions"
      :loading="props.loading"
      :theme="$q.dark.isActive ? 'platyp-dark' : 'platyp'"
    />
    <div v-else>
      <div class="text-h6 text-center">{{ t(`stats.emissions_reductions_share.title`) }}</div>
      <div class="text-subtitle1 text-foreground text-center">{{ t('stats.no_data') }}</div>
    </div>
  </div>

  <div v-if="total > 0" class="q-mt-md chart-text">
    <p class="q-mb-xs">{{ t(`stats.emissions_reductions_share.texts.default`) }}</p>
    <p v-if="biggestEmission">
      {{
        t(`stats.emissions_reductions_share.texts.specific`, {
          percentage: formatNumber(biggestEmission.percentage || 0),
          mode: keyLabel(biggestEmission.mode),
        })
      }}
    </p>
  </div>
</template>

<script setup lang="ts">
import ECharts from 'vue-echarts'
import type { EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import { initOptions, MODE_COLORS, MODE_IDEAL_ORDER, updateOptions } from './commons'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import { formatNumber } from 'src/utils/numbers'
import type { CallbackDataParams } from 'echarts/types/dist/shared'
import { useQuasar } from 'quasar'
import type { EmissionReduction } from 'src/models'
// import { MODE_COLORS } from './commons'

const { t, locale } = useI18n()
const $q = useQuasar()
use([SVGRenderer, PieChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  reductions: EmissionReduction[] | null
  height?: number
  loading?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

interface PercentageEmission {
  mode: string
  percentage: number
}

const option = ref<EChartsOption>({})
const total = ref(0)

const totalSavings = computed(() => {
  const recoEmissions = props.reductions || []
  return recoEmissions.reduce((sum, item) => sum + item.reduced, 0)
})

const biggestEmission = computed<PercentageEmission | null>(() => {
  if (total.value < 5) return null
  if (!props.reductions) return null

  const recoEmissions = props.reductions || []
  if (recoEmissions.length === 0) return null

  let biggest: PercentageEmission | null = null
  recoEmissions.forEach((item) => {
    const percentage = totalSavings.value > 0 ? (item.reduced / totalSavings.value) * 100 : 0
    if (!biggest || percentage > biggest.percentage) {
      biggest = { mode: item.mode, percentage }
    }
  })
  return biggest
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

function keyLabel(key: string) {
  if (key === 'null' || key === 'None') {
    return 'N/A'
  }
  // is integer ?
  if (Number.isInteger(Number(key))) {
    return key
  }
  return t(`stats.emissions_reductions_share.labels.${shortKey(key)}`)
}

function initChartOptions() {
  option.value = {}
  total.value = 0
  if (!props.reductions) {
    return
  }

  const recoEmissions = props.reductions || []
  if (recoEmissions.length === 0) {
    return
  }

  recoEmissions.sort((a, b) => (MODE_IDEAL_ORDER[a.mode] ?? 0) - (MODE_IDEAL_ORDER[b.mode] ?? 0))

  total.value = recoEmissions[0]?.total || 0
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
      text: t(`stats.emissions_reductions_share.title`),
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

        const val = formatNumber(p.value as number)
        return `${p.name}<br/><b>${p.percent}%</b> (${val} kgCO₂eq)`
      },
    },
    legend: {
      show: true,
      bottom: 16,
      type: 'scroll',
    },
    series: [
      {
        name: t(`stats.emissions_reductions_share.series`) || '',
        type: 'pie',
        radius: ['40%', '70%'],
        top: 'middle',
        avoidLabelOverlap: true,
        label: {
          show: true,
          position: 'outer',
        },
        data: recoEmissions.map((item) => ({
          name: keyLabel(item.mode),
          value: item.reduced,
        })),
        color: recoEmissions.map((item) => MODE_COLORS[item.mode] || '#FCC447'),
      },
    ],
  }
  option.value = newOption
}

function shortKey(key: string) {
  return key.replace('freq_mod_pro_', '').replace('freq_mod_', '')
}
</script>
