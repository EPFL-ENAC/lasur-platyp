<template>
  <div>
    <q-input
      filled
      v-model="selected.identifier"
      :label="t('participant.identifier') + ' *'"
      class="q-mb-md"
    />
    <q-select
      v-if="selected.data"
      filled
      v-model="selected.data.age_class"
      :label="t('participant.age_class') + ' *'"
      :options="ageClassOptions"
      emit-value
      map-options
      class="q-mb-md"
    />
    <q-input
      v-if="selected.data"
      filled
      v-model.number="selected.data.employment_rate"
      type="number"
      :min="0"
      :max="100"
      :label="t('participant.employment_rate') + ' *'"
      class="q-mb-md"
    />
    <q-input
      v-if="selected.data"
      filled
      v-model.number="selected.data.remote_work_rate"
      type="number"
      :min="0"
      :max="100"
      :label="t('participant.remote_work_rate') + ' *'"
      class="q-mb-md"
    />
    <q-toggle
      v-if="selected.data"
      v-model="selected.data.company_vehicle"
      :label="t('participant.company_vehicle')"
      class="q-mb-md"
    />
  </div>
</template>

<script setup lang="ts">
import type { Participant, ParticipantData } from 'src/models'

interface Props {
  modelValue: Participant | undefined
}

const props = defineProps<Props>()

const { t } = useI18n()

const selected = ref<Participant>(props.modelValue || ({ identifier: '', data: {} } as Participant))

onMounted(() => {})

watch(() => props.modelValue, onInit)

function onInit() {
  selected.value = props.modelValue || ({ identifier: '', data: {} } as Participant)
  if (!selected.value.data) {
    selected.value.data = {} as ParticipantData
  }
}

const ageClassOptions = computed(() => [
  { label: '16-18', value: '16-18' },
  { label: '18-25', value: '18-25' },
  { label: '26-44', value: '26-44' },
  { label: '45-64', value: '45-64' },
  { label: '>=65', value: '>=65' },
])
</script>
