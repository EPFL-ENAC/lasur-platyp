<template>
  <ContentCard class="step-content">
    <ToggleItem
      v-model="survey.record.data.travel_pro"
      :true-label="t('form.yes')"
      :false-label="t('form.no')"
    />
  </ContentCard>
</template>

<script setup lang="ts">
import ToggleItem from '@/components/form/ToggleItem.vue'
import ContentCard from '@/components/form/ContentCard.vue'

const { t } = useI18n()
const survey = useSurvey()
</script>
