<template>
  <ChoiceItem
    :label="t('form.constraints')"
    :options="constraintsOptions"
    v-model="survey.record.data.constraints"
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

const constraintsOptions = computed<Option[]>(() => [
  { value: 'dependent', label: t('form.constraints_option.dependent') },
  { value: 'heavy', label: t('form.constraints_option.heavy') },
  { value: 'night', label: t('form.constraints_option.night') },
  { value: 'disabled', label: t('form.constraints_option.disabled') },
  { value: 'none', label: t('form.constraints_option.none'), exclusive: true },
])
</script>
