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
      <div class="text-h6 text-center">
        {{ t(`stats.emissions_${props.chartTranslationName}.title`) }}
      </div>
      <div class="text-subtitle1 text-foreground text-center">{{ t('stats.no_data') }}</div>
    </div>
  </div>

  <div v-if="total > 0" class="q-mt-md chart-text">
    <q-markdown
      v-if="emissionItemsLabels"
      :src="t(`stats.emissions_${props.chartTranslationName}.texts.specific`, emissionItemsLabels)"
    />
    <q-markdown
      v-else-if="emissionItemsProLabels"
      :src="
        t(`stats.emissions_${props.chartTranslationName}.texts.specific`, emissionItemsProLabels)
      "
    />
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
import { MODE_COLORS } from './commons'
import { useQuasar } from 'quasar'
import { formatNumber } from 'src/utils/numbers'
import type { Emissions } from 'src/models'

const { t, locale } = useI18n()
const $q = useQuasar()
use([SVGRenderer, CustomChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  chartTranslationName: string
  emissions?: Emissions[] | null
  xaxis?: string
  yaxis?: string
  rangeStep?: number
  height?: number
  loading?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

const chart = shallowRef(null)
const option = ref<EChartsOption>({})
const total = ref(0)

watch([() => props.loading], () => {
  if (props.loading) {
    initChartOptions()
  }
})

watch([() => props.height, locale, () => $q.dark.isActive], () => {
  if (!props.loading) {
    initChartOptions()
  }
})

onMounted(() => {
  initChartOptions()
})

const globalAnswersThreshold = 10
const perModeAnswersThreshold = 3

const emissionItems = computed(() => {
  if (props.chartTranslationName.includes('pro')) {
    return null
  }
  if (!props.emissions) return null
  if (total.value < globalAnswersThreshold) return null

  const carEmissions = props.emissions.find((item) => item.mode === 'car')
  const motoEmissions = props.emissions.find((item) => item.mode === 'moto')
  const allJourneys = props.emissions.reduce((sum, item) => sum + item.journeys, 0)
  const allEmissions = props.emissions.reduce((sum, item) => sum + item.emissions, 0)
  const combinedJourneys = (carEmissions?.journeys || 0) + (motoEmissions?.journeys || 0)
  const combinedEmissions = (carEmissions?.emissions || 0) + (motoEmissions?.emissions || 0)

  if (allJourneys === 0 || allEmissions === 0) {
    return null
  }

  return {
    carMotoJourneysPercentage: (combinedJourneys / allJourneys) * 100,
    carMotoEmissionsPercentage: (combinedEmissions / allEmissions) * 100,
  }
})

const emissionItemsLabels = computed(() => {
  const ei = emissionItems.value
  if (!ei) return null

  return {
    carMotoJourneysPercentage: formatNumber(Math.round(ei.carMotoJourneysPercentage)),
    carMotoEmissionsPercentage: formatNumber(Math.round(ei.carMotoEmissionsPercentage)),
  }
})

const emissionItemsPro = computed(() => {
  if (!props.chartTranslationName.includes('pro')) {
    return null
  }
  if (!props.emissions) return null
  if (total.value < globalAnswersThreshold) return null

  const emissions = props.emissions || []

  const planeEmissions = emissions.find((item) => item.mode === 'plane')
  const carEmissions = emissions.find((item) => item.mode === 'car')
  if (!planeEmissions || !carEmissions) return null
  if (
    planeEmissions.total < perModeAnswersThreshold ||
    carEmissions.total < perModeAnswersThreshold
  ) {
    return null
  }

  const totalEmissions = emissions.reduce((sum, item) => sum + item.emissions, 0)
  if (totalEmissions === 0) return null

  return {
    first: planeEmissions,
    second: carEmissions,
    total: totalEmissions,
    withoutFirst: emissions.filter((item) => item.mode !== planeEmissions.mode),
  }
})

const emissionItemsProLabels = computed(() => {
  const eip = emissionItemsPro.value
  if (!eip) return null

  const withoutFirstEmissions = eip.withoutFirst.reduce((sum, item) => sum + item.emissions, 0)
  const withoutFirstJourneys = eip.withoutFirst.reduce((sum, item) => sum + item.journeys, 0)

  return {
    firstPercent: formatNumber(Math.round((eip.first.emissions / eip.total) * 100)),
    firstMode: keyLabel(eip.first.mode),
    firstEmissions: formatNumber(Math.round((eip.first.emissions || 0) / eip.first.journeys)),
    secondPercent: formatNumber(Math.round((eip.second.emissions / eip.total) * 100)),
    secondMode: keyLabel(eip.second.mode),
    remainingEmissions: formatNumber(Math.round(withoutFirstEmissions / withoutFirstJourneys)),
  }
})

function keyLabel(key: string) {
  if (key === 'null' || key === 'None') {
    return 'N/A'
  }
  // is integer ?
  if (Number.isInteger(Number(key))) {
    return key
  }
  return t(`stats.emissions_${props.chartTranslationName}.labels.${shortKey(key)}`)
}

function initChartOptions() {
  option.value = {}
  total.value = 0
  if (!props.emissions) {
    return
  }

  const emissions = props.emissions || []
  if (emissions.length === 0) {
    return
  }

  let ubound = 0
  const preparedData = emissions
    .sort((a, b) => {
      const emaA = a.journeys ? a.emissions / a.journeys : 0
      const emaB = b.journeys ? b.emissions / b.journeys : 0
      return emaB - emaA
    })
    .map((item) => {
      const data = {
        name: keyLabel(item.mode),
        color: MODE_COLORS[shortKey(item.mode)] || MODE_COLORS['default'],
        value: [
          ubound, // 0: start x
          ubound + item.journeys, // 1: end x
          item.journeys ? (item.emissions / item.journeys).toFixed(2) : 0, // 2: height
          keyLabel(item.mode), // 3: label
          item.emissions.toFixed(0), // 4
          item.journeys, // 5
          `${item.distances.toFixed(0)} km`, // 6
        ],
      }
      ubound += item.journeys
      return data
    })

  total.value = emissions[0]?.total || 0

  const newOption: EChartsOption = {
    grid: {
      left: '40',
      right: '20',
      top: '60',
      bottom: '60',
      containLabel: true,
    },
    animation: false,
    height: props.height - 120,
    title: {
      text: t(`stats.emissions_${props.chartTranslationName}.title`),
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
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      formatter: (params: any) => {
        let html = `<div style="font-weight: bold; margin-bottom: 4px;">${params.marker} ${params.name}</div>`

        const indicesToShow = [4, 5, 6]

        indicesToShow.forEach((idx) => {
          const label = params.dimensionNames[idx]
          const value = params.value[idx]

          if (value !== undefined) {
            html += `
              <div style="display: flex; justify-content: space-between; gap: 20px;">
                <span>${label}</span>
                <span style="font-weight: bold;">${value}</span>
              </div>`
          }
        })

        return html
      },
    },
    legend: {
      show: true,
      bottom: 0,
      left: 'center',
      itemGap: 10,
    },
    xAxis: {
      name: props.xaxis || '',
      nameLocation: 'middle',
      nameGap: 20,
      type: 'value',
    },
    yAxis: {
      name: props.yaxis || '',
      nameLocation: 'middle',
      nameGap: 40,
      type: 'value',
    },
    series: preparedData.map((item) => ({
      name: item.name, // This makes the item appear in the legend
      color: item.color!,
      type: 'custom',
      renderItem: function (params, api) {
        const val0 = api.value(0) as number
        const val1 = api.value(1) as number
        const yValue = api.value(2) as number
        const start = api.coord([val0, yValue])
        const size = api.size!([val1 - val0, yValue]) as [number, number]
        const style = api.style()

        return {
          type: 'group',
          children: [
            {
              type: 'rect',
              shape: {
                x: start[0]!,
                y: start[1]!,
                width: size[0]!,
                height: size[1]!,
              },
              style: {
                ...style,
                fill: item.color!,
              },
            },
          ],
        }
      },
      data: [item.value],
      dimensions: [
        'from',
        'to',
        'emissions',
        'label',
        keyLabel('emissions'),
        keyLabel('journeys'),
        keyLabel('distances'),
      ],
      encode: {
        x: [0, 1],
        y: 2,
        tooltip: [4, 5, 6],
        itemName: 3,
      },
    })),
  }
  option.value = newOption
}

function shortKey(key: string) {
  return key.replace('freq_mod_pro_', '').replace('freq_mod_', '')
}
</script>
