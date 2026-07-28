<template>
  <q-markdown
    v-if="message"
    :src="message"
    no-heading-anchor-links
    no-linkify
    class="compact text-caption q-px-md q-pb-md q-mt-sm"
  />
  <div v-else>
    {{ t('stats.no_data') }}
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { EmissionReduction, Frequencies } from 'src/models'
import { useStats } from 'src/stores/stats'
import { formatNumber } from 'src/utils/numbers'

interface Props {
  frequencyKey: string
  reductionKey?: string
  collaboratorsCount?: number | undefined
}

const props = defineProps<Props>()

const { t } = useI18n()
const statsStore = useStats()

const SCALE_FACTOR = 1 / 1000
const unitLabel = computed(() => t('stats.units.tco2eq_per_year'))

function isEmissionReduction(value: unknown): value is EmissionReduction {
  return (
    typeof value === 'object' &&
    value !== null &&
    'mode' in value &&
    typeof value.mode === 'string' &&
    'total' in value &&
    typeof value.total === 'number' &&
    'reduced' in value &&
    typeof value.reduced === 'number'
  )
}

const frequencyData = computed(() => {
  return statsStore.frequencies[props.frequencyKey]
})

const reductionData = computed<EmissionReduction[]>(() => {
  if (!props.reductionKey) {
    return []
  }

  const data =
    statsStore.emissionsReductions[
      props.reductionKey as keyof typeof statsStore.emissionsReductions
    ]

  if (!Array.isArray(data)) {
    return []
  }

  return data.filter(isEmissionReduction)
})

const bestMode = computed(() => {
  const frequencies = frequencyData.value

  if (!frequencies) {
    return null
  }

  let dataset: { name: string; value: number }[] = []
  let total = 0

  if (Array.isArray(frequencies)) {
    dataset = frequencies.map((item: Frequencies) => {
      total = item.total

      return {
        name: keyLabel(item.field),
        value: item.data
          .map((d) => (d.sum === undefined ? d.count : d.sum))
          .reduce((a, b) => a + b, 0),
      }
    })
  } else {
    total = frequencies.total
    dataset = frequencies.data.map((item) => ({
      name: keyLabel(item.value),
      value: item.sum === undefined ? item.count : item.sum,
    }))
  }

  if (!dataset.length || total === 0) {
    return null
  }

  const maxItem = dataset.reduce((max, item) => (item.value > max.value ? item : max))

  return {
    mode: maxItem.name,
    percentage: Math.round((maxItem.value / total) * 100),
  }
})

const bestModeCount = computed(() => {
  const frequencies = frequencyData.value

  if (!frequencies) {
    return null
  }

  let dataset: { name: string; value: number }[] = []

  if (Array.isArray(frequencies)) {
    dataset = frequencies.map((item: Frequencies) => ({
      name: keyLabel(item.field),
      value: item.data
        .map((d) => (d.sum === undefined ? d.count : d.sum))
        .reduce((a, b) => a + b, 0),
    }))
  } else {
    dataset = frequencies.data.map((item) => ({
      name: keyLabel(item.value),
      value: item.count,
    }))
  }

  if (!dataset.length) {
    return null
  }

  const maxItem = dataset.reduce((max, item) => (item.value > max.value ? item : max))

  return maxItem.value || null
})

const bestReduction = computed(() => {
  if (!reductionData.value.length) {
    return null
  }

  const totalReduction = reductionData.value.reduce((sum, item) => sum + item.reduced, 0)

  if (totalReduction === 0) {
    return null
  }

  const maxItem = reductionData.value.reduce((max, item) =>
    item.reduced > max.reduced ? item : max,
  )

  const collaboratorsCount = props.collaboratorsCount ?? 0
  const extrapolatedReduction =
    bestModeCount.value && collaboratorsCount > 0
      ? (maxItem.reduced / bestModeCount.value) * collaboratorsCount
      : null

  return {
    mode: keyLabel(maxItem.mode),
    reduction: maxItem.reduced * SCALE_FACTOR,
    percentage: Math.round((maxItem.reduced / totalReduction) * 100),
    extrapolatedReduction:
      extrapolatedReduction !== null ? extrapolatedReduction * SCALE_FACTOR : null,
  }
})

const bestPhysicalActivity = computed(() => {
  const gainsPerMode = statsStore.journeyEnergyStats?.gains?.gains_per_mode ?? []
  if (!gainsPerMode.length) {
    return null
  }

  const positiveGains = gainsPerMode.filter((item) => item.added_kcal > 0)
  if (!positiveGains.length) {
    return null
  }

  const maxItem = positiveGains.reduce((max, item) =>
    item.added_kcal > max.added_kcal ? item : max,
  )

  const additionalCollaborators =
    statsStore.journeyEnergyStats!.gains.reco_above_who_count -
    statsStore.journeyEnergyStats!.gains.current_above_who_count

  return {
    mode: keyLabel(maxItem.mode),
    collaboratorsCount: Math.max(additionalCollaborators, 0),
  }
})

const message = computed(() => {
  const paragraphs: string[] = []

  if (bestMode.value) {
    paragraphs.push(
      t('stats.sections.mobility_potentials.insights.most_potential', {
        mode: bestMode.value.mode,
        percentage: bestMode.value.percentage,
      }),
    )
  }

  if (bestReduction.value) {
    let secondParagraph = t(
      'stats.sections.mobility_potentials.insights.biggest_emission_reduction',
      {
        mode: bestReduction.value.mode,
        reduction: formatNumber(bestReduction.value.reduction),
        unit: unitLabel.value,
        percentage: bestReduction.value.percentage,
      },
    )

    if (props.collaboratorsCount && bestReduction.value.extrapolatedReduction !== null) {
      secondParagraph +=
        ' ' +
        t('stats.sections.mobility_potentials.insights.biggest_emission_reduction_extrapolation', {
          collaborators_count: formatNumber(props.collaboratorsCount),
          reduction: formatNumber(bestReduction.value.extrapolatedReduction),
          unit: unitLabel.value,
        })
    }

    paragraphs.push(secondParagraph)
  }

  if (bestPhysicalActivity.value) {
    paragraphs.push(
      t('stats.sections.mobility_potentials.insights.biggest_physical_activity_gain', {
        mode: bestPhysicalActivity.value.mode,
        collaborators_count: formatNumber(bestPhysicalActivity.value.collaboratorsCount),
      }),
    )
  }

  return paragraphs.join('\n\n')
})

function keyLabel(key: string) {
  if (key === 'null' || key === 'None') {
    return t('stats.na')
  }

  if (Number.isInteger(Number(key))) {
    return key
  }

  return t(`transportation_modes.${shortKey(key)}`)
}

function shortKey(key: string) {
  return key.replace('freq_mod_pro_', '').replace('freq_mod_', '')
}
</script>
