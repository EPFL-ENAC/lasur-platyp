<template>
  <chart-panel
    :title="t('stats.pt_pass_reco.title')"
    :description="t('stats.pt_pass_reco.texts.default')"
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
import type { EChartsOption } from 'echarts'
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
import { ptPassLabels, type EquipmentsStats, type PtPassRecommendation } from '@/models'

const { t, locale } = useI18n()
use([SVGRenderer, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

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

const option = ref<EChartsOption>({})

// The "other" bucket is a catch-all for pass types the toolkit does not name:
// only show it when it actually holds somebody.
const rows = computed<PtPassRecommendation[]>(() => {
  const recommendations = props.equipmentsStats?.pt_pass_recommendations ?? []
  const byPassType = new Map(recommendations.map((item) => [item.pass_type, item]))
  return ptPassLabels
    .map(
      (passType) =>
        byPassType.get(passType) ?? {
          pass_type: passType,
          recommended: 0,
          already_equipped: null,
        },
    )
    .filter((item) => item.pass_type !== 'other' || item.recommended > 0)
})

const total = computed(() => rows.value.reduce((sum, item) => sum + item.recommended, 0))

const hasData = computed(() => total.value > 0)

// Passes with no matching equipment option in the collect form: an empty
// inner bar there means "not collected", not "nobody is equipped".
const unknownEquipmentLabels = computed(() =>
  rows.value
    .filter((item) => item.recommended > 0 && item.already_equipped == null)
    .map((item) => keyLabel(item.pass_type)),
)

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

watch([() => props.height, locale, () => props.equipmentsStats], () => {
  if (!props.loading) {
    initChartOptions()
  }
})

onMounted(() => {
  initChartOptions()
})

function keyLabel(passType: string) {
  return t(`stats.pt_pass_reco.labels.${passType}`)
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

function initChartOptions() {
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
</script>
