<template>
  <chart-panel
    :title="t('stats.modal_evolution.title')"
    :description="t('stats.modal_evolution.description')"
    :inline="inline"
  >
    <q-toolbar v-if="!inline" class="chart-toolbar">
      <q-space />
      <q-btn flat icon="more_vert">
        <q-menu>
          <q-list style="min-width: 200px">
            <q-item clickable v-close-popup @click="onToggleModalType">
              <q-item-section side>
                <q-icon :name="stats.modalEvolutionModalType === 'simple' ? 'pie_chart' : 'lens'" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{
                  stats.modalEvolutionModalType === 'simple'
                    ? t('stats.freq_mod.modal_split.detailed')
                    : t('stats.freq_mod.modal_split.simple')
                }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item clickable v-close-popup @click="onChartDownload">
              <q-item-section side>
                <q-icon name="download" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ t('download') }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-menu>
      </q-btn>
    </q-toolbar>
    <e-charts-shell
      ref="shellRef"
      :height="height"
      :loading="props.loading"
      :has-data="hasData"
      :show-table="false"
      :no-data-title="chartTitle"
      :option="option"
      :exportable="!!exportable"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from '@/components/charts/ChartPanel.vue'
import EChartsShell from './EChartsShell.vue'
import type { EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { SankeyChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import { TitleComponent, TooltipComponent } from 'echarts/components'
import { COMPLEX_LABELS_COLORS, GROUP_COLORS, labelColor, SIMPLE_LABELS_COLORS } from './commons'

const { t, te, locale } = useI18n()
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

const isDetailed = computed(() => stats.modalEvolutionModalType === 'detailed')

// Modes are simple typology labels (TP, MA, MA+TP, ...) or, in detailed mode,
// complex typology labels (car, tp, car+tp, ...)
const modeTransitions = computed(() => {
  const results = stats.comparisonResults
  return isDetailed.value ? results?.mode_transitions_complex_labels : results?.mode_transitions
})

const transitions = computed(() => modeTransitions.value?.data ?? [])

const hasData = computed(() => transitions.value.length > 0)

// same title in both modes: qualify it with the typology the chart is rendering
const chartTitle = computed(() => {
  const modalSplit = isDetailed.value
    ? t('stats.freq_mod.modal_split.detailed')
    : t('stats.freq_mod.modal_split.simple')
  return `${t('stats.modal_evolution.title')} (${modalSplit.toLowerCase()})`
})

watch(
  () => props.loading,
  () => {
    if (!props.loading) {
      initChartOptions()
    }
  },
)

watch([() => props.height, locale, isDetailed], () => {
  if (!props.loading) {
    initChartOptions()
  }
})

onMounted(() => {
  initChartOptions()
})

function onToggleModalType() {
  stats.modalEvolutionModalType = isDetailed.value ? 'simple' : 'detailed'
}

function onChartDownload() {
  shellRef.value?.handleExport()
}

function modeLabel(mode: string) {
  if (isDetailed.value) {
    // fall back to the mode vocabulary rather than showing the raw i18n key
    const messageKey = `complex_labels.${mode}`
    return te(messageKey) ? t(messageKey) : t(`transportation_modes.${mode}`)
  }
  return t(`transportation_modes.${mode}`)
}

function modeColor(mode: string) {
  const colors = isDetailed.value ? COMPLEX_LABELS_COLORS : SIMPLE_LABELS_COLORS
  return labelColor(colors, mode) || colors.default || '#ccc'
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

  if (!hasData.value) {
    return
  }

  // Stage (group) order, inferred from the order transitions were emitted in
  // (source_group of the first transition is stage 0, and so on).
  const groupOrder: string[] = []
  transitions.value.forEach((transition) => {
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
        itemStyle: { color: modeColor(mode) },
      })
    }
  }
  transitions.value.forEach((transition) => {
    addNode(transition.source_group, transition.source_mode)
    addNode(transition.target_group, transition.target_mode)
  })

  const links = transitions.value.map((transition) => ({
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
      subtext: t('stats.total', { count: modeTransitions.value?.total ?? 0 }),
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
        // node value is the number of participants flowing through it
        return `${modeLabel(modeFromNodeId(params.name || ''))}<br/><b>${params.value}</b>`
      },
    },
    series: [
      {
        type: 'sankey',
        top: 60,
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
