<template>
  <ChoiceItem
    :label="t('form.equipments')"
    :options="equipmentsOptions"
    v-model="survey.record.data.equipments"
    multiple
    :option-label-class="q.screen.lt.sm ? 'text-h5' : ''"
  />
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar'
import ChoiceItem from 'src/components/form/ChoiceItem.vue'
import type { Option } from 'src/components/form/models'

const { t } = useI18n()
const survey = useSurvey()
const q = useQuasar()

const equipmentsOptions = computed<Option[]>(() => [
  { value: 'bike', label: t('form.equipments_option.bike') },
  { value: 'ebike', label: t('form.equipments_option.ebike') },
  { value: 'upt_subs', label: t('form.equipments_option.upt_subs') },
  { value: 'train_subs', label: t('form.equipments_option.train_subs') },
  { value: 'mob_subs', label: t('form.equipments_option.mob_subs') },
  { value: 'moto', label: t('form.equipments_option.moto') },
  { value: 'car', label: t('form.equipments_option.car') },
  { value: 'ev', label: t('form.equipments_option.ev') },
])
</script>
