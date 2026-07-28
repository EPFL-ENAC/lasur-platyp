<template>
  <q-card flat>
    <q-card-section>
      <q-checkbox
        v-model="survey.record.data.terms_conditions"
        :label="t('form.terms_conditions')"
        size="xl"
        color="primary"
        class="text-h6"
      />
      <div class="text-h6 q-ml-xl">
        <a
          href="https://modus-ge.ch/mobilyse-cgu-collaborateur-trice-s"
          target="_blank"
          rel="noopener noreferrer"
          class="text-muted q-ml-sm"
        >
          {{ t('form.terms_conditions_link') }}
          <q-icon name="open_in_new" size="xs" />
        </a>
      </div>
    </q-card-section>
  </q-card>
  <q-card flat class="q-mt-md">
    <q-card-section>
      <q-checkbox
        v-model="survey.record.data.confidentiality"
        :label="t('form.confidentiality')"
        size="xl"
        color="primary"
        class="text-h6"
      />
      <div class="text-h6 q-ml-xl">
        <a
          href="https://modus-ge.ch/mobilyse-notice-protection-des-donnees"
          target="_blank"
          class="text-muted q-ml-sm"
          rel="noopener noreferrer"
        >
          {{ t('form.confidentiality_link') }}
          <q-icon name="open_in_new" size="xs" />
        </a>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
const { t } = useI18n()
const survey = useSurvey()
</script>
