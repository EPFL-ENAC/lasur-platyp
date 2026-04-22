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
      <div class="text-h6 text-center">{{ t(`stats.behavior_change_${props.type}.title`) }}</div>
      <div class="text-subtitle1 text-foreground text-center">{{ t('stats.no_data') }}</div>
    </div>
  </div>

  <div v-if="total > 0" class="q-mt-md chart-text">
    <p class="q-mb-xs">{{ t(`stats.behavior_change_${props.type}.texts.info`) }}</p>
    <q-markdown :src="chartDescription" />
  </div>
</template>

<script setup lang="ts">
import ECharts from 'vue-echarts'
import type { EChartsOption, SeriesOption } from 'echarts'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { SVGRenderer } from 'echarts/renderers'
import { CATEGORY_COLORS, initOptions, MOTIVATION_COLORS, updateOptions } from './commons'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import { formatNumber } from 'src/utils/numbers'
import type { CallbackDataParams } from 'echarts/types/dist/shared'
import { useQuasar } from 'quasar'
import { lowerCaseFirst } from 'src/utils/string'
import { moveToStart } from 'src/utils/arrays'
import type { BehaviorChangeStats } from 'src/models'

const { t, locale } = useI18n()
use([SVGRenderer, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])
const $q = useQuasar()

interface Props {
  type: 'levers' | 'motivation'
  behaviorChangeStats: BehaviorChangeStats | null
  height?: number
  loading?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

const chart = shallowRef(null)
const option = ref<EChartsOption>({})
const total = ref(0)

const chartDescription = computed(() => {
  if (total.value < 5) {
    return t(`stats.behavior_change_${props.type}.texts.default`)
  }

  if (props.type === 'motivation') {
    return t(`stats.behavior_change_${props.type}.texts.specific`, descriptionValues.value)
  }

  return `${t(`stats.behavior_change_${props.type}.texts.default`)}\n\n${t(
    `stats.behavior_change_${props.type}.texts.specific`,
    descriptionValues.value,
  )}`
})

const descriptionValues = computed(() => {
  if (props.type === 'levers') {
    const levers = props.behaviorChangeStats?.levers
    if (!levers) {
      return {}
    }

    const mostNeededLever = levers.by_mode_levers
      .flatMap((item) => item.levers.map((lever) => ({ ...lever, mode: item.mode })))
      .sort((a, b) => b.count - a.count)[0]
    if (!mostNeededLever) {
      return {}
    }

    return {
      lever: keyLabel(mostNeededLever.category),
    }
  }

  const motivation = props.behaviorChangeStats?.motivation
  if (!motivation) {
    return {}
  }

  const motivatedByMode = motivation.by_mode_motivation.map((item) => {
    return item.motivations.filter((m) => m.level >= 4).reduce((sum, m) => sum + m.percentage, 0)
  })
  return {
    percentage: formatNumber(
      motivatedByMode.reduce((sum, p) => sum + p, 0) / motivatedByMode.length,
    ),
  }
})

watch([() => props.loading], () => {
  if (props.loading) {
    initChartOptions()
  }
})

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
  return t(`stats.behavior_change_${props.type}.labels.${shortKey(key)}`)
}

function initChartOptions() {
  option.value = {}
  total.value = 0

  const opt = props.type === 'levers' ? leversOptions() : motivationOptions()
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
    height: props.height - 100,
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
          return formatNumber(params.value as number)
        },
      },
      data: sorted.map((item) => {
        const lever = item.levers.find((l) => l.category === category)
        return lever ? lever.count : 0
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
          return formatNumber(Math.round(params.value as number))
        },
      },
      data: sorted.map((item) => {
        const lever = item.motivations.find((l) => l.level === level)
        return lever ? lever.count : 0
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
    copy.find((item) => item.mode === 'allModes'),
  )
  moveToStart(
    copy,
    copy.find((item) => item.mode === 'Total'),
  )
  moveToStart(
    copy,
    copy.find((item) => item.mode === 'other'),
  )
  moveToStart(
    copy,
    copy.find((item) => item.mode === 'Autres'),
  )

  return copy
}
</script>
