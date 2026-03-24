<template>
  <div :style="`height: ${height}px; width: 100%;`">
    <template
      v-if="total > 0"
    >
      <e-charts
        ref="chart"
        autoresize
        :init-options="initOptions"
        :option="option"
        :update-options="updateOptions"
        :loading="stats.loading"
      />
      <div>
        <p>{{ t(`stats.${props.type}.texts.default`) }}</p>
        <p>{{ t(`stats.${props.type}.texts.specific`, { mode: keyLabel(mostRecommended.name) }) }}</p>
      </div>
    </template>
    <div v-else>
      <div class="text-h6 text-center">{{ t(`stats.${props.type}.title`) }}</div>
      <div class="text-subtitle1 text-grey-8 text-center">{{ t('stats.no_data') }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ECharts from 'vue-echarts'
import type { EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { SankeyChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import { initOptions, updateOptions } from './commons'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import type { Links } from 'src/models'
import { MODE_COLORS } from './commons'

const { t, locale } = useI18n()
const stats = useStats()
use([SVGRenderer, SankeyChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  type: string
  height?: number
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

interface RecommendedMode {
  name: string
  value: number
}

const chart = shallowRef(null)
const option = ref<EChartsOption>({})
const total = ref(0)
const mostRecommended = ref<RecommendedMode>({
  name: '',
  value: -Infinity
})

watch(
  () => stats.loading,
  () => {
    if (stats.loading) {
      initChartOptions()
    }
  },
)

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
  return t(`stats.${props.type}.labels.${shortKey(key)}`)
}

function initChartOptions() {
  const recoSuffix = ' '
  option.value = {}
  total.value = 0
  if (!stats.links || !stats.links[props.type]) {
    return
  }

  const links = stats.links[props.type] as Links
  if (links.data.length === 0) {
    return
  }
  total.value = links.total || 0
  const linksData = links.data.map((item) => ({
    source: keyLabel(item.source),
    target: keyLabel(item.target) + recoSuffix,
    value: item.value,
  }))

  const recommendations: Record<string, number> = {};

  const nodes = new Set<string>()
  links.data.forEach((item) => {
    nodes.add(item.source)
    nodes.add(item.target + '_reco')

    recommendations[item.target] = (recommendations[item.target] ?? 0) + item.value
  })

  Object.entries(recommendations).forEach(([mode, value]) => {
    if (value > mostRecommended.value.value) {
      mostRecommended.value = {
        name: mode,
        value,
      }
    }
  })

  const newOption: EChartsOption = {
    grid: {
      left: '0',
      right: '0',
      top: '40',
      bottom: '0',
    },
    animation: false,
    height: props.height - 80,
    title: {
      text: t(`stats.${props.type}.title`),
      subtext: t(`stats.total`, { count: total.value }),
      left: 'center',
      top: 0,
      textStyle: {
        fontSize: 16,
      },
    },
    legend: {
      show: false,
    },
    tooltip: {
      trigger: 'item',
      triggerOn: 'mousemove',
    },
    series: [
      {
        type: 'sankey',
        top: 60,
        emphasis: {
          focus: 'adjacency',
        },
        data: Array.from(nodes).map((key) => ({
          name: key.endsWith('_reco')
            ? keyLabel(key.replace('_reco', '')) + recoSuffix
            : keyLabel(key),
          itemStyle: {
            color: MODE_COLORS[key.replace('_reco', '')] || MODE_COLORS.default || '#ccc',
          },
        })),
        links: linksData,
      },
    ],
  }
  option.value = newOption
}

function shortKey(key: string) {
  return key.replace('freq_mod_pro_', '').replace('freq_mod_', '')
}
</script>
