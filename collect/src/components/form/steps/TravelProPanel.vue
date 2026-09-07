<template>
  <div>
    <ToggleItem
      v-model="survey.record.data.travel_pro"
      :label="t('form.travel_pro')"
      label-class="question-label text-bold q-mb-lg"
      :true-label="t('form.yes')"
      :false-label="t('form.no')"
    />
  </div>
</template>

<script setup lang="ts">
import ToggleItem from '@/components/form/ToggleItem.vue'

const { t } = useI18n()
const survey = useSurvey()
</script>
