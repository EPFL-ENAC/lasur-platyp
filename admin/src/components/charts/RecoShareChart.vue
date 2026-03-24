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
    />
    <div v-else>
      <div class="text-h6 text-center">{{ t(`stats.emissions_reco_share.title`) }}</div>
      <div class="text-subtitle1 text-grey-8 text-center">{{ t('stats.no_data') }}</div>
    </div>
  </div>

  <div>
    <p>{{ t(`stats.emissions_reco_share.texts.default`) }}</p>
    <p v-if="biggestEmission">
      {{ t(`stats.emissions_reco_share.texts.specific`, { percentage: toMaxDecimals(biggestEmission.percentage || 0, 2), mode: keyLabel(biggestEmission.mode) }) }}
    </p>
  </div>
</template>

<script setup lang="ts">
import ECharts from 'vue-echarts'
import type { EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { CustomChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import { initOptions, updateOptions } from './commons'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import { toMaxDecimals } from 'src/utils/numbers'
import type { CallbackDataParams } from 'echarts/types/dist/shared'
// import { MODE_COLORS } from './commons'

const { t, locale } = useI18n()
const stats = useStats()
use([SVGRenderer, CustomChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  reco: string
  height?: number
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
  const recoEmissions = stats.emissions?.[props.reco] || []
  return recoEmissions.reduce((sum, item) => sum + item.emissions, 0)
})

const biggestEmission = computed<PercentageEmission | null>(() => {
  if (total.value < 5) return null
  if (!stats.emissions || !stats.emissions[props.reco]) return null

  const recoEmissions = stats.emissions[props.reco] || []
  if (recoEmissions.length === 0) return null

  let biggest: PercentageEmission | null = null
  recoEmissions.forEach((item) => {
    const percentage = totalSavings.value > 0 ? (item.emissions / totalSavings.value) * 100 : 0
    if (!biggest || percentage > biggest.percentage) {
      biggest = { mode: item.mode, percentage }
    }
  })
  return biggest
})

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
  return t(`stats.emissions_reco_share.labels.${shortKey(key)}`)
}

function initChartOptions() {
  option.value = {}
  total.value = 0
  if (!stats.emissions || !stats.emissions[props.reco]) {
    return
  }

  const recoEmissions = stats.emissions[props.reco] || []
  if (recoEmissions.length === 0) {
    return
  }

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
      text: t(`stats.emissions_reco_share.title`),
      subtext: t(`stats.total`, { count: total.value }),
      left: 'center',
      top: 0,
      itemGap: 10,
      textStyle: {
        fontSize: 16,
      },
    },
    tooltip: {
      trigger: "item",
      formatter: function (params: CallbackDataParams | CallbackDataParams[]) {
        const p = Array.isArray(params) ? params[0] : params
        if (!p) return ''

        const val = new Intl.NumberFormat().format(
          toMaxDecimals(p.value as number, 0) || 0
        );
        return `${p.name}<br/><b>${val} kgCO₂eq</b> (${p.percent}%)`;
      },
    },
    legend: {
      show: true,
      bottom: 16,
      type: 'scroll',
    },
    series: [
      {
        name: 'Emissions',
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
            return new Intl.NumberFormat().format(toMaxDecimals(params.value as number, 2) || 0)
          },
        },
        data: recoEmissions.map((item) => ({
          name: keyLabel(item.mode),
          value: item.emissions,
        })),
      },
    ],
  }
  option.value = newOption
}

function shortKey(key: string) {
  return key.replace('freq_mod_pro_', '').replace('freq_mod_', '')
}
</script>
