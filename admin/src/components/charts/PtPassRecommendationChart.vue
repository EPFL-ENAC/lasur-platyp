<template>
  <chart-panel
    :title="t('stats.pt_pass_reco.title')"
    :description="descriptionText"
    :chart-info-text="chartInfoText"
    :inline="inline"
  >
    <div>
      <q-toolbar v-if="!inline" class="chart-toolbar">
        <q-space />
        <q-btn flat icon="more_vert">
          <q-menu>
            <q-list style="min-width: 200px">
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
        :show-table="inline"
        :no-data-title="t('stats.pt_pass_reco.title')"
        :option="option"
        :exportable="!inline"
      />
    </div>
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from '@/components/charts/ChartPanel.vue'
import EChartsShell from './EChartsShell.vue'
import type { EChartsOption, SeriesOption } from 'echarts'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import type { CallbackDataParams } from 'echarts/types/dist/shared'
import { formatNumber } from '@/utils/numbers'
import { GROUP_COLORS } from './commons'
import { ptPassLabels, type EquipmentsStats, type PtPassRecommendation } from '@/models'

const { t, locale } = useI18n()
use([SVGRenderer, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

const stats = useStats()
const isComparison = computed(() => !!stats.comparisonMode)

interface Props {
  equipmentsStats: EquipmentsStats | null
  height?: number
  loading?: boolean
  inline?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

type EChartsShellExposed = {
  handleExport: () => Promise<void>
}

const shellRef = useTemplateRef<EChartsShellExposed>('shellRef')

function onChartDownload() {
  shellRef.value?.handleExport()
}

// Public transport blue (MODE_COLORS.tpu) for the participants already
// equipped, a tint of it outlined in the same hue for the recommendations
// they sit inside of.
const RECOMMENDED_COLOR = '#e2eef6'
const RECOMMENDED_BORDER_COLOR = '#99c7df'
const EQUIPPED_COLOR = '#99c7df'
// Comparison bars are colored per group: the recommendations the group is not
// equipped for are the same color, faded, stacked above the equipped ones.
const NOT_EQUIPPED_OPACITY = 0.4

const option = ref<EChartsOption>({})

interface PassRow {
  pass_type: string
  recommended: number
  already_equipped: number | null
}

interface ComparisonGroupRows {
  name: string
  color: string
  /** Participants the shares are computed on, i.e. the records the stats cover. */
  participants: number
  rows: PassRow[]
}

/**
 * All pass types, in chart order, whether or not the payload carries them.
 * `already_equipped` is missing from the payload when it is unknown: null
 * fields are stripped from the stats responses.
 */
function toRows(recommendations: PtPassRecommendation[] | undefined): PassRow[] {
  const byPassType = new Map((recommendations ?? []).map((item) => [item.pass_type, item]))
  return ptPassLabels.map((passType) => {
    const item = byPassType.get(passType)
    return {
      pass_type: passType,
      recommended: item?.recommended ?? 0,
      already_equipped: item?.already_equipped ?? null,
    }
  })
}

function rowOf(group: ComparisonGroupRows, passType: string): PassRow {
  return (
    group.rows.find((row) => row.pass_type === passType) ?? {
      pass_type: passType,
      recommended: 0,
      already_equipped: null,
    }
  )
}

function percentOf(value: number, total: number) {
  return total > 0 ? Number(((value / total) * 100).toFixed(2)) : 0
}

// The "other" bucket is a catch-all for pass types the toolkit does not name:
// only show it when it actually holds somebody.
const rows = computed<PassRow[]>(() =>
  toRows(props.equipmentsStats?.pt_pass_recommendations).filter(
    (item) => item.pass_type !== 'other' || item.recommended > 0,
  ),
)

const comparisonGroups = computed<ComparisonGroupRows[]>(() =>
  (stats.comparisonResults?.groups ?? []).map((group, index) => ({
    name: group.name,
    color: GROUP_COLORS[index % GROUP_COLORS.length] ?? '#ccc',
    // Shares are of the participants the equipment statistics are computed on,
    // not of every record of the group.
    participants: group.equipments_stats?.total ?? group.total,
    rows: toRows(group.equipments_stats?.pt_pass_recommendations),
  })),
)

const comparisonPassTypes = computed(() =>
  ptPassLabels.filter(
    (passType) =>
      passType !== 'other' ||
      comparisonGroups.value.some((group) => rowOf(group, passType).recommended > 0),
  ),
)

const total = computed(() => rows.value.reduce((sum, item) => sum + item.recommended, 0))

const hasData = computed(() => {
  if (isComparison.value) {
    return comparisonGroups.value.some((group) => group.rows.some((row) => row.recommended > 0))
  }
  return total.value > 0
})

const descriptionText = computed(() =>
  isComparison.value
    ? t('stats.pt_pass_reco.texts.comparison')
    : t('stats.pt_pass_reco.texts.default'),
)

// Passes with no matching equipment option in the collect form: an empty
// inner bar there means "not collected", not "nobody is equipped".
const unknownEquipmentLabels = computed(() => {
  if (isComparison.value) {
    return comparisonPassTypes.value
      .filter((passType) =>
        comparisonGroups.value.some((group) => {
          const row = rowOf(group, passType)
          return row.recommended > 0 && row.already_equipped === null
        }),
      )
      .map((passType) => keyLabel(passType))
  }
  return rows.value
    .filter((item) => item.recommended > 0 && item.already_equipped === null)
    .map((item) => keyLabel(item.pass_type))
})

const chartInfoText = computed(() => {
  if (!unknownEquipmentLabels.value.length) {
    return ''
  }
  return t('stats.pt_pass_reco.texts.equipped_unknown_note', {
    passes: unknownEquipmentLabels.value.join(', '),
  })
})

defineExpose({
  handleExport: () => shellRef.value?.handleExport(),
  get chartInfoText() {
    return chartInfoText.value
  },
})

watch(
  () => props.loading,
  () => {
    if (props.loading) {
      initChartOptions()
    }
  },
)

watch(
  [
    () => props.height,
    locale,
    () => props.equipmentsStats,
    () => stats.comparisonResults,
    () => stats.comparisonMode,
  ],
  () => {
    if (!props.loading) {
      initChartOptions()
    }
  },
)

onMounted(() => {
  initChartOptions()
})

function keyLabel(passType: string) {
  return t(`stats.pt_pass_reco.labels.${passType}`)
}

/** Group name followed by its participants count, as the other comparison charts do. */
function groupLabel(group: ComparisonGroupRows) {
  return `${group.name} (${t('stats.total', { count: group.participants })})`
}

function tooltipFormatter(params: CallbackDataParams | CallbackDataParams[]) {
  const items = Array.isArray(params) ? params : [params]
  const first = items[0]
  if (!first) return ''

  const row = rows.value[first.dataIndex]
  if (!row) return ''

  const lines = [
    `<b>${keyLabel(row.pass_type)}</b>`,
    t('stats.pt_pass_reco.tooltip.recommended', { count: formatNumber(row.recommended) }),
  ]
  // Pass types whose equipment is not collected have no count to show: the
  // line is dropped altogether, the panel footnote explains why.
  const equipped = row.already_equipped
  if (equipped !== null && equipped !== undefined) {
    const percentage = row.recommended > 0 ? (equipped / row.recommended) * 100 : 0
    lines.push(
      t('stats.pt_pass_reco.tooltip.equipped', {
        count: formatNumber(equipped),
        percentage: formatNumber(percentage),
      }),
    )
  }
  return lines.join('<br />')
}

function comparisonTooltipFormatter(params: CallbackDataParams | CallbackDataParams[]) {
  const items = Array.isArray(params) ? params : [params]
  const first = items[0]
  if (!first) return ''

  const passType = comparisonPassTypes.value[first.dataIndex]
  if (!passType) return ''

  // Built from the datasets rather than from the hovered series: each group
  // draws two of them (equipped and the rest), and the counts behind the
  // percentages are not in the series data.
  const lines = [`<b>${keyLabel(passType)}</b>`]
  comparisonGroups.value.forEach((group) => {
    const row = rowOf(group, passType)
    const marker = `<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background-color:${group.color}"></span>`
    const parts = [
      t('stats.pt_pass_reco.tooltip.group_recommended', {
        count: formatNumber(row.recommended),
        percentage: formatNumber(percentOf(row.recommended, group.participants)),
      }),
    ]
    const equipped = row.already_equipped
    if (equipped !== null && equipped !== undefined) {
      parts.push(
        t('stats.pt_pass_reco.tooltip.group_equipped', {
          count: formatNumber(equipped),
          percentage: formatNumber(row.recommended > 0 ? (equipped / row.recommended) * 100 : 0),
        }),
      )
    }
    lines.push(`${marker}${group.name}: ${parts.join(', ')}`)
  })
  return lines.join('<br />')
}

function initChartOptions() {
  if (isComparison.value) {
    initComparisonChartOptions()
    return
  }

  option.value = {}

  if (!hasData.value) {
    return
  }

  option.value = {
    grid: {
      left: '20',
      right: '20',
      top: '60',
      bottom: '60',
      containLabel: true,
    },
    animation: false,
    height: props.height - 100,
    title: {
      text: t('stats.pt_pass_reco.title'),
      subtext: t('stats.total', { count: total.value }),
      left: 'center',
      top: 0,
      itemGap: 10,
      textStyle: {
        fontSize: 16,
      },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
      formatter: tooltipFormatter,
    },
    legend: {
      show: true,
      bottom: 0,
      data: [t('stats.pt_pass_reco.recommended'), t('stats.pt_pass_reco.equipped')],
    },
    xAxis: {
      name: t('stats.pt_pass_reco.xaxis'),
      nameLocation: 'middle',
      nameGap: 30,
      type: 'category',
      data: rows.value.map((item) => keyLabel(item.pass_type)),
    },
    yAxis: {
      name: t('stats.nb_employees'),
      nameLocation: 'end',
      nameGap: 20,
      type: 'value',
      minInterval: 1,
    },
    series: [
      {
        name: t('stats.pt_pass_reco.recommended'),
        type: 'bar',
        data: rows.value.map((item) => item.recommended),
        itemStyle: {
          color: RECOMMENDED_COLOR,
          borderColor: RECOMMENDED_BORDER_COLOR,
          borderWidth: 1,
        },
      },
      {
        name: t('stats.pt_pass_reco.equipped'),
        type: 'bar',
        // Drawn inside the recommended bar: the equipped are a subset of it.
        // A null value leaves the bar empty, for the pass types whose
        // equipment is not collected.
        barGap: '-100%',
        data: rows.value.map((item) => item.already_equipped),
        itemStyle: {
          color: EQUIPPED_COLOR,
        },
        z: 3,
      },
    ],
  }
}

function initComparisonChartOptions() {
  option.value = {}

  const groups = comparisonGroups.value
  const passTypes = comparisonPassTypes.value
  if (!hasData.value || !passTypes.length) {
    return
  }

  const participants = groups.reduce((sum, group) => sum + group.participants, 0)

  // Groups do not have the same size, so the bars carry shares of each group's
  // participants: one bar per group and per pass type, its solid part the
  // participants already equipped, stacked under the rest of the
  // recommendations so the whole bar is the recommended share.
  const series: SeriesOption[] = groups.flatMap((group, index) => {
    const name = groupLabel(group)
    const stack = `group-${index}`
    return [
      {
        name,
        type: 'bar' as const,
        stack,
        color: group.color,
        data: passTypes.map((passType) => {
          const row = rowOf(group, passType)
          return row.already_equipped === null
            ? null
            : percentOf(row.already_equipped, group.participants)
        }),
      },
      {
        // Named apart from the solid part, so that the table listing one column
        // per series tells the two halves of the bar apart. The legend keeps a
        // single entry per group, see legend.data below.
        name: t('stats.pt_pass_reco.not_equipped_series', { group: group.name }),
        type: 'bar' as const,
        stack,
        color: group.color,
        itemStyle: { opacity: NOT_EQUIPPED_OPACITY },
        data: passTypes.map((passType) => {
          const row = rowOf(group, passType)
          return percentOf(row.recommended - (row.already_equipped ?? 0), group.participants)
        }),
      },
    ]
  })

  option.value = {
    grid: {
      left: '20',
      right: '20',
      top: '60',
      bottom: '60',
      containLabel: true,
    },
    animation: false,
    height: props.height - 100,
    title: {
      text: t('stats.pt_pass_reco.title'),
      subtext: t('stats.total', { count: participants }),
      left: 'center',
      top: 0,
      itemGap: 10,
      textStyle: {
        fontSize: 16,
      },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
      formatter: comparisonTooltipFormatter,
    },
    legend: {
      show: true,
      bottom: 0,
      type: 'scroll',
      // A colour key, one entry per group: hiding a group would only hide half
      // of its (stacked) bar, which reads as a smaller group rather than none.
      selectedMode: false,
      data: groups.map((group) => groupLabel(group)),
    },
    xAxis: {
      name: t('stats.pt_pass_reco.xaxis'),
      nameLocation: 'middle',
      nameGap: 30,
      type: 'category',
      data: passTypes.map((passType) => keyLabel(passType)),
    },
    yAxis: {
      name: t('stats.percent_employees'),
      nameLocation: 'end',
      nameGap: 20,
      type: 'value',
    },
    series,
  }
}
</script>
