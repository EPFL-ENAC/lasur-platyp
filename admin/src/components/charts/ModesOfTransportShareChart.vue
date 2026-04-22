<template>
  <div :style="`height: ${height}px; width: 100%;`">
    <e-charts
      v-if="hasData"
      ref="chart"
      autoresize
      :init-options="initOptions"
      :option="option"
      :update-options="updateOptions"
      :loading="props.loading"
      :theme="$q.dark.isActive ? 'platyp-dark' : 'platyp'"
    />
    <div v-else>
      <div class="text-h6 text-center">{{ t(`stats.freq_mod.title`) }}</div>
      <div class="text-subtitle1 text-foreground text-foreground text-center">
        {{ t('stats.no_data') }}
      </div>
    </div>
  </div>

  <div v-if="total > 0" class="q-mt-md chart-text">
    <p v-if="topModes.length === 3" class="q-mb-xs">
      {{
        t('stats.freq_mod.texts.specific', {
          top_1: topModes[0],
          top_2: topModes[1],
          top_3: topModes[2],
        })
      }}
    </p>
    <p>{{ t('stats.freq_mod.texts.default') }}</p>
  </div>
</template>

<script setup lang="ts">
import ECharts from 'vue-echarts'
import type { EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import { initOptions, updateOptions } from './commons'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import type { Frequencies } from 'src/models'
import { MODE_COLORS } from './commons'
import { useQuasar } from 'quasar'

const { t, locale } = useI18n()
const $q = useQuasar()
use([SVGRenderer, PieChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  frequencies: Frequencies | Frequencies[] | null
  loading?: boolean
  height?: number
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

const chart = shallowRef(null)
const option = ref<EChartsOption>({})
const total = ref(0)
const topModes = ref<string[]>([])

const hasData = computed(() => {
  if (!props.frequencies) {
    return false
  }
  return Array.isArray(props.frequencies)
    ? props.frequencies.length > 0
    : props.frequencies.data.length > 0
})

watch(
  () => props.loading,
  () => {
    if (props.loading) {
      initChartOptions()
    }
  },
)

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
  return t(`stats.freq_mod.labels.${shortKey(key)}`)
}

const MRMT_VALUES = {
  bike: 13.6,
  walking: 20.7,
  pub: 21,
  moto: 8.2,
  car: 36.5,
}

function initChartOptions() {
  option.value = {}
  total.value = 0
  if (!props.frequencies) {
    return
  }

  let dataset: { key: string; name: string; value: number; count: number }[] = []
  if (Array.isArray(props.frequencies)) {
    dataset = (props.frequencies as Frequencies[]).map((item: Frequencies) => {
      total.value = item.total
      return {
        key: shortKey(item.field),
        name: keyLabel(item.field),
        count: item.data.reduce((a, b) => a + b.count, 0),
        value: item.data
          .map((d) => (d.sum === undefined ? d.count : d.sum))
          .reduce((a, b) => a + b, 0),
      }
    })
  } else {
    const frequencies = props.frequencies as Frequencies
    dataset = frequencies.data.map((item) => ({
      key: shortKey(item.value),
      name: keyLabel(item.value),
      count: item.count,
      value: item.sum === undefined ? item.count : item.sum,
    }))
    total.value = frequencies.total
  }

  const sortedByValue = dataset
    .filter((item) => item.count > 5)
    .toSorted((a, b) => b.value - a.value)
  topModes.value = sortedByValue.slice(0, 3).map((item) => item.name)

  // Extract category names and values for series
  const categories = dataset.map((item) => item.key)
  const colors = categories.map((category) => MODE_COLORS[category] || '#ccc')

  if (categories.length === 0) {
    return
  }

  const mrmtDataset = Object.entries(MRMT_VALUES).map(([key, value]) => ({
    key,
    name: keyLabel(key),
    value,
  }))

  const mrmtColors = mrmtDataset.map((item) => MODE_COLORS[item.key] || '#ccc')

  const newOption: EChartsOption = {
    grid: {
      left: '20',
      right: '20',
      top: '40',
      bottom: '20',
      containLabel: true,
    },
    animation: false,
    height: props.height,
    title: {
      text: t(`stats.freq_mod.title`),
      subtext: t(`stats.total`, { count: total.value }),
      left: 'center',
      top: 0,
      textStyle: {
        fontSize: 16,
      },
    },
    tooltip: {
      trigger: 'item',
      formatter: '<b>{b}</b><br/>{c} ({d}%)',
    },
    legend: {
      show: true,
      bottom: 0,
      left: 'center',
    },
    series: [
      {
        type: 'pie',
        radius: ['30%', '50%'],
        center: ['30%', '50%'],
        avoidLabelOverlap: true,
        color: colors,
        label: {
          margin: 0,
          fontWeight: 'bold',
          formatter: '{d}% ({c})',
        },
        data: dataset,
      },
      {
        name: 'mrmt',
        type: 'pie',
        radius: ['12%', '20%'],
        center: ['80%', '68%'],
        avoidLabelOverlap: true,
        color: mrmtColors,
        tooltip: {
          formatter: '<b>{b}</b><br/>{d}%',
        },
        label: {
          formatter: '{d}% (MRMT)',
          fontSize: 10,
        },
        data: mrmtDataset,
      },
    ],
  }
  option.value = newOption
}

function shortKey(key: string) {
  return key.replace('freq_mod_pro_', '').replace('freq_mod_', '')
}
</script>
