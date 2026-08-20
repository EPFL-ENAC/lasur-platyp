<template>
  <chart-panel
    :title="t('stats.modal_evolution.title')"
    :description="t('stats.modal_evolution.description')"
    :inline="inline"
  >
    <e-charts-shell
      ref="shellRef"
      :height="height"
      :loading="props.loading"
      :has-data="hasData"
      :show-table="false"
      :no-data-title="t('stats.modal_evolution.title')"
      :option="option"
      :exportable="!!exportable"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from 'src/components/charts/ChartPanel.vue'
import EChartsShell from './EChartsShell.vue'
import type { EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { SankeyChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import { TitleComponent, TooltipComponent } from 'echarts/components'
import { GROUP_COLORS, MODE_COLORS } from './commons'

const { t, locale } = useI18n()
use([SVGRenderer, SankeyChart, TitleComponent, TooltipComponent])

interface Props {
  height?: number
  loading?: boolean
  exportable?: boolean
  inline?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
  exportable: true,
})

type EChartsShellExposed = {
  handleExport: () => Promise<void>
}

defineExpose({
  handleExport: () => shellRef.value?.handleExport(),
})

const shellRef = useTemplateRef<EChartsShellExposed>('shellRef')

const stats = useStats()
const option = ref<EChartsOption>({})

const hasData = computed(() => (stats.comparisonResults?.mode_transitions?.length ?? 0) > 0)

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

function modeLabel(mode: string) {
  return t(`transportation_modes.${mode}`)
}

function nodeId(group: string, mode: string) {
  return `${group}::${mode}`
}

function modeFromNodeId(id: string) {
  return id.split('::').slice(1).join('::')
}

interface SankeyNode {
  name: string
  depth: number
  itemStyle: { color: string }
}

function initChartOptions() {
  option.value = {}

  const transitions = stats.comparisonResults?.mode_transitions ?? []
  if (transitions.length === 0) {
    return
  }

  // Stage (group) order, inferred from the order transitions were emitted in
  // (source_group of the first transition is stage 0, and so on).
  const groupOrder: string[] = []
  transitions.forEach((transition) => {
    if (!groupOrder.includes(transition.source_group)) {
      groupOrder.push(transition.source_group)
    }
    if (!groupOrder.includes(transition.target_group)) {
      groupOrder.push(transition.target_group)
    }
  })

  const nodes = new Map<string, SankeyNode>()
  const addNode = (group: string, mode: string) => {
    const id = nodeId(group, mode)
    if (!nodes.has(id)) {
      nodes.set(id, {
        name: id,
        depth: groupOrder.indexOf(group),
        itemStyle: { color: MODE_COLORS[mode] || MODE_COLORS.default || '#ccc' },
      })
    }
  }
  transitions.forEach((transition) => {
    addNode(transition.source_group, transition.source_mode)
    addNode(transition.target_group, transition.target_mode)
  })

  const links = transitions.map((transition) => ({
    source: nodeId(transition.source_group, transition.source_mode),
    target: nodeId(transition.target_group, transition.target_mode),
    value: transition.count,
    lineStyle: {
      color:
        GROUP_COLORS[groupOrder.indexOf(transition.source_group) % GROUP_COLORS.length] ?? '#ccc',
      opacity: 0.4,
    },
  }))

  option.value = {
    animation: false,
    height: props.height,
    title: {
      text: t('stats.modal_evolution.title'),
      left: 'center',
      top: 0,
      textStyle: { fontSize: 16 },
    },
    tooltip: {
      trigger: 'item',
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      formatter: (params: any) => {
        if (params.dataType === 'edge') {
          const sourceMode = modeLabel(modeFromNodeId(params.data.source))
          const targetMode = modeLabel(modeFromNodeId(params.data.target))
          return `${sourceMode} → ${targetMode}<br/><b>${params.value}</b>`
        }
        return modeLabel(modeFromNodeId(params.name || ''))
      },
    },
    series: [
      {
        type: 'sankey',
        emphasis: { focus: 'adjacency' },
        data: Array.from(nodes.values()),
        links,
        label: {
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          formatter: (params: any) => modeLabel(modeFromNodeId(params.name as string)),
        },
      },
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    ] as any,
  }
}
</script>
