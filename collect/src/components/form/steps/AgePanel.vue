<template>
  <ChoiceItem
    :label="t('form.age_class')"
    :options="ageOptions"
    v-model="survey.record.data.age_class"
    :option-label-class="q.screen.lt.sm ? 'text-h5' : ''"
  />
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar'
import type { Option } from 'src/components/form/models'
import ChoiceItem from 'src/components/form/ChoiceItem.vue'

const { t } = useI18n()
const survey = useSurvey()
const q = useQuasar()

const ageOptions = computed<Option[]>(() => [
  { value: '16-24', label: t('form.age_class_option.16_24') },
  { value: '25-44', label: t('form.age_class_option.25_44') },
  { value: '45-64', label: t('form.age_class_option.45_64') },
  { value: '65+', label: t('form.age_class_option.65') },
])
</script>
