<template>
  <div v-if="option.series" :style="`height: ${height}px; width: 100%;`">
    <e-charts
      ref="chart"
      autoresize
      :init-options="initOptions"
      :option="option"
      :update-options="updateOptions"
      :loading="stats.loading"
    />
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

const { t } = useI18n()
const stats = useStats()
use([SVGRenderer, SankeyChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  type: string
  height?: number
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

const chart = shallowRef(null)
const option = ref<EChartsOption>({})

watch(
  () => stats.loading,
  () => {
    if (stats.loading) {
      initChartOptions()
    }
  },
)

watch([() => props.height], () => {
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
  if (!stats.links || !stats.links[props.type]) {
    return
  }

  const links = stats.links[props.type] as Links
  if (links.data.length === 0) {
    return
  }
  const total = links.total || 0
  const linksData = links.data.map((item) => ({
    source: keyLabel(item.source),
    target: keyLabel(item.target) + recoSuffix,
    value: item.value,
  }))
  const nodes = new Set<string>()
  links.data.forEach((item) => {
    nodes.add(item.source)
    nodes.add(item.target + '_reco')
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
      subtext: t(`stats.total`, { count: total }),
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
