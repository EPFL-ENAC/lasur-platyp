<template>
  <div :style="`height: ${height}px; width: 100%;`">
    <e-charts
      v-if="total > 0"
      ref="chart"
      autoresize
      :init-options="initOptions"
      :option="option"
      :update-options="updateOptions"
      :loading="stats.loading"
      theme="platyp"
    />
    <div v-else>
      <div class="text-h6 text-center">{{ t(`stats.behavior_change_${props.type}.title`) }}</div>
      <div class="text-subtitle1 text-grey-8 text-center">{{ t('stats.no_data') }}</div>
    </div>
  </div>

  <div>
    <p>{{ t(`stats.behavior_change_${props.type}.texts.default`) }}</p>
    <q-markdown
      v-if="total > 5"
      :src="t(`stats.behavior_change_${props.type}.texts.specific`, descriptionValues)"
    />
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
import { toMaxDecimals } from 'src/utils/numbers'
import type { CallbackDataParams } from 'echarts/types/dist/shared'

const { t, locale } = useI18n()
const stats = useStats()
use([SVGRenderer, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  type: 'levers' | 'motivation'
  height?: number
}
const props = withDefaults(defineProps<Props>(), {
  height: 400,
})

const chart = shallowRef(null)
const option = ref<EChartsOption>({})
const total = ref(0)

const descriptionValues = computed(() => {
  if (props.type === 'levers') {
    const levers = stats.behaviorChange.levers
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

  const motivation = stats.behaviorChange.motivation
  if (!motivation) {
    return {}
  }

  const motivatedByMode = motivation.by_mode_motivation.map((item) => {
    return item.motivations.filter((m) => m.level >= 4).reduce((sum, m) => sum + m.percentage, 0)
  })
  return {
    percentage: toMaxDecimals(
      motivatedByMode.reduce((sum, p) => sum + p, 0) / motivatedByMode.length,
      2,
    ),
  }
})

watch([() => stats.loading], () => {
  if (stats.loading) {
    initChartOptions()
  }
})

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
  const behaviorChangeData = stats.behaviorChange.levers
  if (!behaviorChangeData) {
    return null
  }
  const allCategories = new Set<string>(
    behaviorChangeData.by_mode_levers.flatMap((item) => item.levers.map((lever) => lever.category)),
  )

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
          return new Intl.NumberFormat().format(toMaxDecimals(params.value as number, 2) || 0)
        },
      },
      data: behaviorChangeData.by_mode_levers.map((item) => {
        const lever = item.levers.find((l) => l.category === category)
        return lever ? lever.count : 0
      }),
      itemStyle: {
        color: CATEGORY_COLORS[category] || '#ccc',
      },
    })) as SeriesOption[],
    categories: behaviorChangeData.by_mode_levers.map((item) => keyLabel(item.mode)),
    total: behaviorChangeData.total_responses,
  }
}

function motivationOptions() {
  const behaviorChangeData = stats.behaviorChange.motivation
  if (!behaviorChangeData) {
    return null
  }
  const levels = [1, 2, 3, 4, 5]

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
          return new Intl.NumberFormat().format(toMaxDecimals(params.value as number, 2) || 0)
        },
      },
      data: behaviorChangeData.by_mode_motivation.map((item) => {
        const lever = item.motivations.find((l) => l.level === level)
        return lever ? lever.count : 0
      }),
      itemStyle: {
        color: MOTIVATION_COLORS[level] || '#ccc',
      },
    })) as SeriesOption[],
    categories: behaviorChangeData.by_mode_motivation.map((item) => keyLabel(item.mode)),
    total: behaviorChangeData.total_responses,
  }
}

function shortKey(key: string) {
  return key.replace('freq_mod_pro_', '').replace('freq_mod_', '')
}
</script>
