<template>
  <div>
    <div class="text-bold q-mb-md question-label">
      {{ t('form.intermodality_pro') }}
    </div>
    <div class="question-hint q-mb-md">{{ t('form.intermodality_pro_hint') }}</div>
    <template v-for="(journey, idx) in journeys" :key="idx">
      <q-card flat class="q-mb-md">
        <q-card-section>
          <!-- A plain flex row rather than a toolbar: the toolbar brought its own
          horizontal padding and fixed height, which indented the hint away from
          the card content it introduces. -->
          <div class="journey-card__header">
            <div class="question-hint">{{ t('form.journey_pro.hint') }}</div>
            <q-btn
              round
              :title="t('form.journey_pro.remove')"
              :aria-label="t('form.journey_pro.remove')"
              icon="close"
              color="accent"
              @click="onRemoveJourney(idx)"
            />
          </div>
          <ProJourneyItem
            v-if="journeys[idx]"
            v-model="journeys[idx]"
            :map-id="`map-pro-${idx}`"
            :modes="modes"
            :option-label-class="q.screen.lt.sm ? 'text-h5' : 'text-h5'"
          />
        </q-card-section>
      </q-card>
    </template>
    <q-btn
      flat
      no-caps
      icon="add"
      :label="t('form.journey_pro.add')"
      class="picker-option picker-option--dashed picker-option--block"
      @click="onAddJourney"
    />
  </div>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar'
import ProJourneyItem from '@/components/form/steps/ProJourneyItem.vue'
import type { ProJourney } from '@/models'

const { t } = useI18n()
const q = useQuasar()

interface Props {
  modelValue: ProJourney[]
  modes: string[]
}
const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const journeys = computed({
  get: () => props.modelValue || [],
  set: (val: ProJourney[]) => {
    emit('update:modelValue', val)
  },
})

function onAddJourney() {
  if (!journeys.value) {
    journeys.value = []
  }
  journeys.value.push({
    days: 1,
    days_per: 'year',
    mode: '',
    location: undefined,
    constraints: [],
  })
}

function onRemoveJourney(idx: number) {
  if (journeys.value) {
    journeys.value.splice(idx, 1)
  }
}
</script>

<style scoped lang="scss">
// The hint starts on the card's own content edge, with the remove button
// pinned to the opposite one and both aligned to the first line of text.
.journey-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}
</style>
