<template>
  <ToggleItem
    :label="t('form.travel_pro')"
    v-model="survey.record.data.travel_pro"
    :left-label="t('form.no')"
    :right-label="t('form.yes')"
  />
</template>

<script setup lang="ts">
import ToggleItem from 'src/components/form/ToggleItem.vue'

const { t } = useI18n()
const survey = useSurvey()
</script>
