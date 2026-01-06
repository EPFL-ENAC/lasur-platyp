<template>
  <div>
    <NumberItem
      :label="t('form.employment_rate')"
      v-model="survey.record.data.employment_rate"
      :min="0"
      :max="100"
      :step="5"
      unit="%"
      class="q-mb-lg"
    />
    <NumberItem
      :label="t('form.remote_work_rate')"
      v-model="survey.record.data.remote_work_rate"
      :min="0"
      :max="100"
      :step="5"
      unit="%"
      class="q-mb-lg"
    />
    <ToggleItem
      :label="t('form.company_vehicle')"
      :left-label="t('form.no')"
      :right-label="t('form.yes')"
      v-model="survey.record.data.company_vehicle"
      class="q-mb-lg"
    />
  </div>
</template>

<script setup lang="ts">
import NumberItem from 'src/components/form/NumberItem.vue'
import ToggleItem from 'src/components/form/ToggleItem.vue'

const { t } = useI18n()
const survey = useSurvey()
</script>
