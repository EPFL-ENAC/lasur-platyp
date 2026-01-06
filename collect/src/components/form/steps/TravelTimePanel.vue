<template>
  <NumberItem
    :label="t('form.travel_time')"
    v-model="survey.record.data.travel_time"
    :min="5"
    :max="120"
    :step="5"
    :unit-hint="t('form.travel_time_minutes')"
  />
</template>

<script setup lang="ts">
import NumberItem from 'src/components/form/NumberItem.vue'

const { t } = useI18n()
const survey = useSurvey()
</script>
