<template>
  <div>
    <e-charts-shell
      ref="shellRef"
      :height="height"
      :loading="props.loading"
      :has-data="total > 0"
      :show-table="!exportable"
      :no-data-title="t(`stats.behavior_change_${props.type}.title`)"
      :option="option"
      :exportable="!!exportable"
    />
    <q-markdown v-if="props.description" compact :src="props.description" class="q-mt-sm" />
  </div>
</template>

<script setup lang="ts">
import EChartsShell from './EChartsShell.vue'
import type { EChartsOption, SeriesOption } from 'echarts'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import { CATEGORY_COLORS, MOTIVATION_COLORS } from './commons'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import { formatNumber } from 'src/utils/numbers'
import type { CallbackDataParams, XAXisOption } from 'echarts/types/dist/shared'
import { lowerCaseFirst } from 'src/utils/string'
import { moveToStart } from 'src/utils/arrays'
import type { BehaviorChangeStats } from 'src/models'

const { t, locale } = useI18n()
use([SVGRenderer, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

const stats = useStats()
const isComparison = computed(() => !!stats.comparisonMode)

interface Props {
  type: 'levers' | 'motivation'
  behaviorChangeStats: BehaviorChangeStats | null
  height?: number
  loading?: boolean
  percent?: boolean
  exportable?: boolean
  description?: string
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

const option = ref<EChartsOption>({})
const total = ref(0)

watch([() => props.loading], () => {
  if (props.loading) {
    initChartOptions()
  }
})

watch([() => props.height, locale, () => props.percent], () => {
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
  return t(`stats.behavior_change_${props.type}.labels.${shortKey(key)}`)
}

function initChartOptions() {
  option.value = {}
  total.value = 0

  const opt = isComparison.value
    ? props.type === 'levers'
      ? comparisonLeversOptions()
      : comparisonMotivationOptions()
    : props.type === 'levers'
      ? leversOptions()
      : motivationOptions()
  if (!opt) {
    return
  }

  total.value = opt.total

  const newOption: EChartsOption = {
    grid: {
      left: '40',
      right: '20',
      top: '60',
      bottom: '20',
      containLabel: true,
    },
    animation: false,
    height: props.height - 140,
    title: {
      text: t(`stats.behavior_change_${props.type}.title`),
      subtext: t(`stats.total`, { count: total.value }),
      left: 'center',
      top: 0,
      itemGap: 10,
      textStyle: {
        fontSize: 16,
      },
    },
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      show: true,
      bottom: 16,
    },
    xAxis: {
      type: 'value',
    },
    yAxis: {
      type: 'category',
      data: opt.categories,
    },
    series: opt.series,
  }
  if (props.percent) {
    ;(newOption.xAxis as XAXisOption).max = 100
  }
  option.value = newOption
}

function leversOptions() {
  const behaviorChangeData = props.behaviorChangeStats?.levers
  if (!behaviorChangeData) {
    return null
  }
  const allCategories = new Set<string>(
    behaviorChangeData.by_mode_levers.flatMap((item) => item.levers.map((lever) => lever.category)),
  )

  const sorted = getSortedModes(behaviorChangeData.by_mode_levers)

  return {
    series: Array.from(allCategories).map((category) => ({
      name: keyLabel(category),
      type: 'bar',
      stack: 'total',
      label: {
        show: true,
        position: 'inside',
        formatter: function (params: CallbackDataParams) {
          if (params.value === 0) {
            return ''
          }
          if (props.percent) {
            return `${formatNumber(params.value as number)}%`
          }
          return formatNumber(params.value as number)
        },
      },
      data: sorted.map((item) => {
        const lever = item.levers.find((l) => l.category === category)
        if (!lever) {
          return 0
        }
        return props.percent ? lever.percentage : lever.count
      }),
      itemStyle: {
        color: CATEGORY_COLORS[category] || '#ccc',
      },
    })) as SeriesOption[],
    categories: sorted.map((item) => keyLabel(item.mode)),
    total: behaviorChangeData.total_responses,
  }
}

function motivationOptions() {
  const behaviorChangeData = props.behaviorChangeStats?.motivation
  if (!behaviorChangeData) {
    return null
  }
  const levels = [1, 2, 3, 4, 5]

  const sorted = getSortedModes(behaviorChangeData.by_mode_motivation)

  return {
    series: levels.map((level) => ({
      name: keyLabel(`l${level.toString()}`),
      type: 'bar',
      stack: 'total',
      label: {
        show: true,
        position: 'inside',
        formatter: function (params: CallbackDataParams) {
          if (params.value === 0) {
            return ''
          }
          if (props.percent) {
            return `${formatNumber(params.value as number)}%`
          }
          return formatNumber(Math.round(params.value as number))
        },
      },
      data: sorted.map((item) => {
        const lever = item.motivations.find((l) => l.level === level)
        if (!lever) {
          return 0
        }
        return props.percent ? lever.percentage : lever.count
      }),
      itemStyle: {
        color: MOTIVATION_COLORS[level] || '#ccc',
      },
    })) as SeriesOption[],
    categories: sorted.map((item) => keyLabel(item.mode)),
    total: behaviorChangeData.total_responses,
  }
}

function shortKey(key: string) {
  return lowerCaseFirst(key.replace('freq_mod_pro_', '').replace('freq_mod_', ''))
}

function getSortedModes<
  T extends
    | BehaviorChangeStats['levers']['by_mode_levers']
    | BehaviorChangeStats['motivation']['by_mode_motivation'],
>(data: T): T {
  const copy = [...data] as T

  moveToStart(
    copy,
    copy.find((item) => item.mode === 'other'),
  )
  moveToStart(
    copy,
    copy.find((item) => item.mode === 'Autres'),
  )
  moveToStart(
    copy,
    copy.find((item) => item.mode === 'allModes'),
  )
  moveToStart(
    copy,
    copy.find((item) => item.mode === 'Total'),
  )

  return copy
}

function orderModes(modes: string[]): string[] {
  const copy = [...modes]
  moveToStart(
    copy,
    copy.find((mode) => mode === 'other'),
  )
  moveToStart(
    copy,
    copy.find((mode) => mode === 'Autres'),
  )
  moveToStart(
    copy,
    copy.find((mode) => mode === 'allModes'),
  )
  moveToStart(
    copy,
    copy.find((mode) => mode === 'Total'),
  )
  return copy
}

function comparisonLeversOptions() {
  const groups = (stats.comparisonResults?.groups ?? []).map((group) => ({
    name: group.name,
    byMode: group.behavior_change?.levers?.by_mode_levers ?? [],
    total: group.behavior_change?.levers?.total_responses ?? 0,
  }))
  if (groups.every((group) => group.byMode.length === 0)) {
    return null
  }

  const modes = orderModes(
    Array.from(new Set(groups.flatMap((group) => group.byMode.map((item) => item.mode)))),
  )
  const categories = Array.from(
    new Set(
      groups.flatMap((group) =>
        group.byMode.flatMap((item) => item.levers.map((lever) => lever.category)),
      ),
    ),
  )
  if (modes.length === 0 || categories.length === 0) {
    return null
  }

  const series: SeriesOption[] = []
  groups.forEach((group, groupIndex) => {
    categories.forEach((category) => {
      series.push({
        name: `${group.name} — ${keyLabel(category)}`,
        type: 'bar',
        stack: `group_${groupIndex}`,
        emphasis: { focus: 'series' },
        itemStyle: { color: CATEGORY_COLORS[category] || '#ccc' },
        data: modes.map((mode) => {
          const modeItem = group.byMode.find((item) => item.mode === mode)
          const lever = modeItem?.levers.find((l) => l.category === category)
          if (!lever) return 0
          return props.percent ? lever.percentage : lever.count
        }),
      })
    })
  })

  return {
    series,
    categories: modes.map((mode) => keyLabel(mode)),
    total: groups.reduce((sum, group) => sum + group.total, 0),
  }
}

function comparisonMotivationOptions() {
  const groups = (stats.comparisonResults?.groups ?? []).map((group) => ({
    name: group.name,
    byMode: group.behavior_change?.motivation?.by_mode_motivation ?? [],
    total: group.behavior_change?.motivation?.total_responses ?? 0,
  }))
  if (groups.every((group) => group.byMode.length === 0)) {
    return null
  }

  const modes = orderModes(
    Array.from(new Set(groups.flatMap((group) => group.byMode.map((item) => item.mode)))),
  )
  if (modes.length === 0) {
    return null
  }
  const levels = [1, 2, 3, 4, 5]

  const series: SeriesOption[] = []
  groups.forEach((group, groupIndex) => {
    levels.forEach((level) => {
      series.push({
        name: `${group.name} — ${keyLabel(`l${level.toString()}`)}`,
        type: 'bar',
        stack: `group_${groupIndex}`,
        emphasis: { focus: 'series' },
        itemStyle: { color: MOTIVATION_COLORS[level] || '#ccc' },
        data: modes.map((mode) => {
          const modeItem = group.byMode.find((item) => item.mode === mode)
          const motivation = modeItem?.motivations.find((m) => m.level === level)
          if (!motivation) return 0
          return props.percent ? motivation.percentage : motivation.count
        }),
      })
    })
  })

  return {
    series,
    categories: modes.map((mode) => keyLabel(mode)),
    total: groups.reduce((sum, group) => sum + group.total, 0),
  }
}
</script>
