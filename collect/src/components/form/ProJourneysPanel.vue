<template>
  <div>
    <div class="text-bold q-mb-md text-h4">
      {{ t('form.intermodality_pro') }}
    </div>
    <div class="text-h6 q-mb-md">{{ t('form.intermodality_pro_hint') }}</div>
    <template v-for="(journey, idx) in journeys" :key="idx">
      <q-card class="bg-primary q-mb-md">
        <q-card-section>
          <q-toolbar>
            <div class="on-left text-h6 q-pt-xs">{{ t('form.journey_pro.hint') }}</div>
            <q-space />
            <q-btn
              round
              :title="t('form.journey_pro.remove')"
              icon="close"
              color="accent"
              @click="onRemoveJourney(idx)"
            />
          </q-toolbar>
          <ProJourneyItem
            v-if="journeys[idx]"
            v-model="journeys[idx]"
            :modes="modes"
            :option-label-class="q.screen.lt.sm ? 'text-h5' : 'text-h5'"
          />
        </q-card-section>
      </q-card>
    </template>
    <q-btn icon="add" :label="t('form.journey_pro.add')" color="accent" @click="onAddJourney" />
  </div>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar'
import ProJourneyItem from 'src/components/form/ProJourneyItem.vue'
import type { ProJourney } from 'src/models'

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
    mode: '',
    hex_id: undefined,
  })
}

function onRemoveJourney(idx: number) {
  if (journeys.value) {
    journeys.value.splice(idx, 1)
  }
}
</script>
