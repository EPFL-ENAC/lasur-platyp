<template>
  <NumberItem
    :label="t('form.travel_time')"
    label-class="text-h4 text-bold q-mb-lg"
    v-model="survey.record.data.travel_time"
    :min="5"
    :max="120"
    :step="5"
    :unit-hint="t('form.travel_time_minutes')"
  />
</template>

<script setup lang="ts">
import NumberItem from '@/components/form/NumberItem.vue'

const { t } = useI18n()
const survey = useSurvey()
</script>
