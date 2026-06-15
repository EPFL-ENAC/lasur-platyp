<template>
  <div>
    <LocationItem
      map-id="origin-map"
      :label="t('form.origin')"
      :hint="t('form.origin_hint')"
      v-model="survey.record.data.origin"
      class="q-mt-xl"
    />
  </div>
</template>

<script setup lang="ts">
import LocationItem from 'src/components/form/LocationItem.vue'

const { t } = useI18n()
const survey = useSurvey()
</script>
