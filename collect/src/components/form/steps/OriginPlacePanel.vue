<template>
  <ContentCard class="step-content">
    <LocationItem
      map-id="origin-map"
      :hint="t('form.origin_hint')"
      v-model="survey.record.data.origin"
    />
  </ContentCard>
</template>

<script setup lang="ts">
import LocationItem from '@/components/form/LocationItem.vue'
import ContentCard from '@/components/form/ContentCard.vue'

const { t } = useI18n()
const survey = useSurvey()
</script>
