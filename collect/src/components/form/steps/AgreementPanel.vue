<template>
  <div class="bg-primary rounded-borders q-pa-md q-mt-lg">
    <q-checkbox
      v-model="survey.record.data.terms_conditions"
      :label="t('form.terms_conditions')"
      size="xl"
      color="green-6"
      class="text-h6"
    />
    <div class="text-h6 q-ml-xl">
      <a href="https://modus-ge.ch/toolkit-cgu" target="_blank" class="text-secondary q-ml-sm">
        {{ t('form.terms_conditions_link') }}
        <q-icon name="open_in_new" size="xs" />
      </a>
    </div>
  </div>
  <div class="bg-primary rounded-borders q-pa-md q-mt-lg">
    <q-checkbox
      v-model="survey.record.data.confidentiality"
      :label="t('form.confidentiality')"
      size="xl"
      color="green-6"
      class="text-h6"
    />
    <div class="text-h6 q-ml-xl">
      <a
        href="https://modus-ge.ch/toolkit-privacy-notice"
        target="_blank"
        class="text-secondary q-ml-sm"
      >
        {{ t('form.confidentiality_link') }}
        <q-icon name="open_in_new" size="xs"
      /></a>
    </div>
  </div>
</template>

<script setup lang="ts">
const { t } = useI18n()
const survey = useSurvey()
</script>
