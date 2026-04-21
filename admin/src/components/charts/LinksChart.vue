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
      :data-chart-id="chartId"
    />
    <div v-else>
      <div class="text-h6 text-center">{{ t(`stats.${props.type}.title`) }}</div>
      <div class="text-subtitle1 text-foreground text-center">{{ t('stats.no_data') }}</div>
    </div>
  </div>

  <div class="q-mt-md chart-text" :data-chart-id="chartId">
    <p class="q-mb-xs">{{ t(`stats.${props.type}.texts.default`) }}</p>
    <p v-if="mostRecommendedTarget">
      {{
        t(`stats.${props.type}.texts.specific`, { mode: keyLabel(mostRecommendedTarget.target) })
      }}
    </p>
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
import type { StatLinks } from 'src/models'
import { MODE_COLORS } from './commons'
import { useQuasar } from 'quasar'
import { getRandomId } from 'src/utils/random'

const { t, locale } = useI18n()
const $q = useQuasar()
use([SVGRenderer, SankeyChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  type: string
  links: StatLinks | null
  height?: number
  loading?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

const chart = shallowRef(null)
const chartId = getRandomId()
const option = ref<EChartsOption>({})
const total = ref(0)

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

const mostRecommendedTarget = computed(() => {
  if (total.value < 5) return null
  const links = props.links
  if (!links) return null

  return links.most_recommended_target
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
  if (!props.links) {
    return
  }

  const links = props.links
  if (links.data.length === 0) {
    return
  }
  total.value = links.total ?? 0
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
