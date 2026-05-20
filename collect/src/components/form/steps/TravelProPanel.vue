<template>
  <div>
    <ToggleItem
      v-model="survey.record.data.travel_pro"
      required
      :label="t('form.travel_pro')"
      label-class="text-h4 text-bold q-mb-lg"
      :left-label="t('form.no')"
      :right-label="t('form.yes')"
    />
  </div>
</template>

<script setup lang="ts">
import ToggleItem from 'src/components/form/ToggleItem.vue'

const { t } = useI18n()
const survey = useSurvey()
</script>
