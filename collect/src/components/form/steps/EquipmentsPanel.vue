<template>
  <ChoiceItem
    :label="t('form.equipments')"
    :options="equipmentsOptions"
    v-model="survey.record.data.equipments"
    multiple
    :option-label-class="q.screen.lt.sm ? 'text-h5' : ''"
    @update:model-value="cleanupEquipments"
  />
  <q-input
    v-if="survey.record.data.equipments.includes('other')"
    :label="t('form.equipments_option.other')"
    v-model="survey.record.data.equipments_custom"
    type="textarea"
    color="field"
    bg-color="field"
    outlined
    rounded
    dense
  />
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar'
import ChoiceItem from '@/components/form/ChoiceItem.vue'
import type { Option } from '@/components/form/models'

const { t } = useI18n()
const survey = useSurvey()
const q = useQuasar()

const equipmentsOptions = computed<Option[]>(() => [
  { value: 'bike', label: t('form.equipments_option.bike') },
  { value: 'ebike', label: t('form.equipments_option.ebike') },
  { value: 'tpu_unireso', label: t('form.equipments_option.tpu_unireso') },
  { value: 'tpu_leman_pass', label: t('form.equipments_option.tpu_leman_pass') },
  { value: 'train_demi_tarif', label: t('form.equipments_option.train_demi_tarif') },
  { value: 'train_abo_gen', label: t('form.equipments_option.train_abo_gen') },
  { value: 'mob_subs', label: t('form.equipments_option.mob_subs') },
  { value: 'moto', label: t('form.equipments_option.moto') },
  { value: 'car', label: t('form.equipments_option.car') },
  { value: 'ev', label: t('form.equipments_option.ev') },
  { value: 'other', label: t('form.equipments_option.other') },
])

function cleanupEquipments() {
  if (!survey.record.data.equipments.includes('other')) {
    survey.record.data.equipments_custom = ''
  }
}
</script>
