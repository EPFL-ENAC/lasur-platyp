<template>
  <e-charts-shell
    ref="shellRef"
    :height="height"
    :loading="props.loading"
    :has-data="total > 0"
    :show-table="!exportable"
    :no-data-title="chartTitle"
    :option="option"
    :exportable="!!exportable"
  />
</template>

<script setup lang="ts">
import EChartsShell from './EChartsShell.vue'
import type { EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { SankeyChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import type { StatLinks } from '@/models'
import { COMPLEX_LABELS_COLORS, MODE_COLORS, SIMPLE_LABELS_COLORS } from './commons'

const { t, te, locale } = useI18n()
use([SVGRenderer, SankeyChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  type: string
  links: StatLinks | null
  // Which typology the links are expressed in: 'simple' links a simple label
  // to a simple recommendation, 'complex' links a complex label to a
  // recommended transport mode. When not set, both ends are transport modes.
  labelType?: 'simple' | 'complex'
  height?: number
  loading?: boolean
  exportable?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
  exportable: true,
})

type EChartsShellExposed = {
  handleExport: () => Promise<void>
}

const shellRef = useTemplateRef<EChartsShellExposed>('shellRef')

const option = ref<EChartsOption>({})
const total = ref(0)

// simple/complex links show the same title: qualify it with the typology the
// chart is currently rendering
const chartTitle = computed(() => {
  const title = t(`stats.${props.type}.title`)
  if (!props.labelType) {
    return title
  }
  const modalSplit =
    props.labelType === 'simple'
      ? t('stats.freq_mod.modal_split.simple')
      : t('stats.freq_mod.modal_split.detailed')
  return `${title} (${modalSplit.toLowerCase()})`
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

const mostRecommendedTarget = computed(() => {
  if (total.value < 5) return null
  const links = props.links
  if (!links) return null

  return links.most_recommended_target
})

defineExpose({
  handleExport: () => shellRef.value?.handleExport(),
  get chartInfoText() {
    if (mostRecommendedTarget.value) {
      return t(`stats.${props.type}.texts.specific`, {
        mode: targetLabel(mostRecommendedTarget.value.target),
      })
    }
    return ''
  },
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

function labelTypeLabel(key: string, labelType: 'simple' | 'complex') {
  if (key === 'null' || key === 'None') {
    return 'N/A'
  }
  const messageKey = `${labelType}_labels.${shortKey(key)}`
  // recommendations may be expressed as a transport mode rather than a
  // typology label: fall back to the mode vocabulary instead of showing the
  // raw i18n key
  return te(messageKey) ? t(messageKey) : keyLabel(key)
}

function labelTypeColor(key: string, labelType: 'simple' | 'complex') {
  const colors = labelType === 'simple' ? SIMPLE_LABELS_COLORS : COMPLEX_LABELS_COLORS
  return labelColor(colors, shortKey(key)) || modeColor(key)
}

/**
 * Typology labels come from the data as-is: match them leniently so an
 * unexpected case ('ma+tp') or component order ('TP+MA') still gets the color
 * of the label it denotes, instead of falling back to the neutral default.
 */
function labelColor(colors: { [key: string]: string }, key: string) {
  if (colors[key]) {
    return colors[key]
  }
  const parts = key.toLowerCase().split('+')
  const match = Object.keys(colors).find((candidate) => {
    const candidateParts = candidate.toLowerCase().split('+')
    return (
      candidateParts.length === parts.length &&
      candidateParts.every((part) => parts.includes(part)) &&
      parts.every((part) => candidateParts.includes(part))
    )
  })
  return match ? colors[match] : undefined
}

function modeColor(key: string) {
  return MODE_COLORS[shortKey(key)] || MODE_COLORS.default || '#ccc'
}

// Link sources are typology labels when labelType is set
function sourceLabel(key: string) {
  return props.labelType ? labelTypeLabel(key, props.labelType) : keyLabel(key)
}

function sourceColor(key: string) {
  return props.labelType ? labelTypeColor(key, props.labelType) : modeColor(key)
}

// Simple links target the simple recommendation, which is a simple label too;
// the other variants target a recommended transport mode
function targetLabel(key: string) {
  return props.labelType === 'simple' ? labelTypeLabel(key, 'simple') : keyLabel(key)
}

function targetColor(key: string) {
  return props.labelType === 'simple' ? labelTypeColor(key, 'simple') : modeColor(key)
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
    source: sourceLabel(item.source),
    target: targetLabel(item.target) + recoSuffix,
    value: item.value,
  }))

  const sourceNodes = new Set<string>()
  const targetNodes = new Set<string>()
  links.data.forEach((item) => {
    sourceNodes.add(item.source)
    targetNodes.add(item.target)
  })
  const nodes = [
    ...Array.from(sourceNodes).map((key) => ({
      name: sourceLabel(key),
      itemStyle: { color: sourceColor(key) },
    })),
    ...Array.from(targetNodes).map((key) => ({
      name: targetLabel(key) + recoSuffix,
      itemStyle: { color: targetColor(key) },
    })),
  ]

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
      text: chartTitle.value,
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
        data: nodes,
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
