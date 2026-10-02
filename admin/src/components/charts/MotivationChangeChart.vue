<template>
  <chart-panel
    :title="chartTitle"
    :description="panelDescription"
    :chart-info-text="chartDescription"
    :inline="inline"
  >
    <q-toolbar v-if="!inline" class="chart-toolbar">
      <q-space />
      <q-btn flat icon="more_vert">
        <q-menu>
          <q-list style="min-width: 200px">
            <q-item clickable v-close-popup @click="onToggleModalType">
              <q-item-section side>
                <q-icon :name="stats.motivationModalType === 'simple' ? 'pie_chart' : 'lens'" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{
                  stats.motivationModalType === 'simple'
                    ? t('stats.freq_mod.modal_split.detailed')
                    : t('stats.freq_mod.modal_split.simple')
                }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item clickable v-close-popup @click="onTogglePercent">
              <q-item-section side>
                <q-icon :name="stats.motivationPercent ? 'check_box' : 'check_box_outline_blank'" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ t('stats.percent_employees') }}</q-item-label>
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
    <behavior-change-chart
      ref="chartRef"
      type="motivation"
      :behavior-change-stats="behaviorChangeStats"
      :height="height"
      :loading="loading"
      :percent="stats.motivationPercent"
      :modal-type="modalType"
      :exportable="!inline"
    />
  </chart-panel>
</template>

<script setup lang="ts">
import ChartPanel from '@/components/charts/ChartPanel.vue'
import BehaviorChangeChart from '@/components/charts/BehaviorChangeChart.vue'
import { formatPercent } from '@/utils/numbers'
import { isSimpleLabel } from '@/utils/modalities'
import { aggregateMotivationBySimpleLabel } from '@/components/charts/commons'
import type { BehaviorChangeByModeMotivation, BehaviorChangeStats } from '@/models'

interface Props {
  height: number
  loading?: boolean
  behaviorChangeStats: BehaviorChangeStats | null
  inline?: boolean
}

const props = defineProps<Props>()

type BehaviorChangeChartExposed = {
  handleExport: () => Promise<void>
}

const chartRef = ref<BehaviorChangeChartExposed | null>(null)

const { t } = useI18n()

const stats = useStats()

const modalType = computed(() => (stats.motivationModalType === 'simple' ? 'simple' : 'detailed'))

const chartTitle = computed(
  () =>
    `${t('stats.behavior_change_motivation.title')} (${t(
      `stats.freq_mod.modal_split.${modalType.value}`,
    ).toLowerCase()})`,
)

function onToggleModalType() {
  stats.motivationModalType = stats.motivationModalType === 'simple' ? 'detailed' : 'simple'
}

function onTogglePercent() {
  stats.motivationPercent = !stats.motivationPercent
}

function onChartDownload() {
  chartRef.value?.handleExport()
}

const total = computed(() => props.behaviorChangeStats?.motivation?.total_responses ?? 0)

// info only for the single-campaign view: comparison mode shows the
// comparison sentence instead.
const panelDescription = computed(() =>
  stats.comparisonMode ? '' : t('stats.behavior_change_motivation.texts.info'),
)

const descriptionValues = computed(() => {
  const motivation = props.behaviorChangeStats?.motivation
  if (!motivation) {
    return {}
  }

  const motivatedByMode = motivation.by_mode_motivation.map(motivatedPercent)
  return {
    percentage: formatPercent(
      motivatedByMode.reduce((sum, p) => sum + p, 0) / motivatedByMode.length,
    ),
  }
})

/** Share of the participants of the row who are rather or very motivated. */
function motivatedPercent(row: BehaviorChangeByModeMotivation) {
  return row.motivations.filter((m) => m.level >= 4).reduce((sum, m) => sum + m.percentage, 0)
}

/** The all modes row: 'Total' when split by mode, 'allModes' otherwise. */
function allModesRow(rows: BehaviorChangeByModeMotivation[] | undefined) {
  return rows?.find((row) => row.mode === 'Total' || row.mode === 'allModes')
}

/** Rows as charted: recommended modes, or the simple labels they fold into. */
function chartedRows(byMode: BehaviorChangeByModeMotivation[] | undefined) {
  if (!byMode) return []
  return modalType.value === 'simple' ? aggregateMotivationBySimpleLabel(byMode) : byMode
}

function modeLabel(mode: string) {
  return isSimpleLabel(mode)
    ? t(`simple_labels.${mode}`)
    : t(`stats.behavior_change_motivation.labels.${mode}`)
}

const comparisonValues = computed(() => {
  const groups = stats.comparisonResults?.groups ?? []
  if (groups.length < 2) return null

  const lastGroup = groups[groups.length - 1]!
  const prevGroup = groups[groups.length - 2]!
  const lastRows = chartedRows(lastGroup.behavior_change?.motivation?.by_mode_motivation)
  const prevRows = chartedRows(prevGroup.behavior_change?.motivation?.by_mode_motivation)

  // The most recommended actual mode: aggregates do not name a recommendation.
  const lastRow = lastRows
    .filter((row) => !['Total', 'allModes', 'Autres', 'other'].includes(row.mode))
    .sort((a, b) => b.response_count - a.response_count)[0]
  const prevRow = prevRows.find((row) => row.mode === lastRow?.mode)
  if (lastRow?.response_count && prevRow?.response_count) {
    return {
      key: 'comparison',
      values: {
        mode: modeLabel(lastRow.mode),
        lastGroup: lastGroup.name,
        prevGroup: prevGroup.name,
        lastPercent: formatPercent(motivatedPercent(lastRow)),
        prevPercent: formatPercent(motivatedPercent(prevRow)),
      },
    }
  }

  // No shared individual mode (e.g. a group whose answers were all aggregated
  // under 'allModes', or whose top mode has no row in the other group): compare
  // the all-modes rows, like the levers chart does.
  const lastAll = allModesRow(lastRows)
  const prevAll = allModesRow(prevRows)
  if (!lastAll?.response_count || !prevAll?.response_count) return null

  return {
    key: 'comparison_all_modes',
    values: {
      lastGroup: lastGroup.name,
      prevGroup: prevGroup.name,
      lastPercent: formatPercent(motivatedPercent(lastAll)),
      prevPercent: formatPercent(motivatedPercent(prevAll)),
    },
  }
})

const chartDescription = computed(() => {
  if (stats.comparisonMode) {
    return comparisonValues.value
      ? t(
          `stats.behavior_change_motivation.texts.${comparisonValues.value.key}`,
          comparisonValues.value.values,
        )
      : t('stats.behavior_change_motivation.texts.default')
  }

  if (total.value < 5) {
    return t('stats.behavior_change_motivation.texts.default')
  }

  return `${t('stats.behavior_change_motivation.texts.default')}\n\n${t(
    'stats.behavior_change_motivation.texts.specific',
    descriptionValues.value,
  )}`
})
</script>
