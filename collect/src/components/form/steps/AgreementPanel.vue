<template>
  <q-card flat>
    <q-card-section>
      <q-checkbox
        v-model="survey.record.data.terms_conditions"
        :label="t('form.terms_conditions')"
        size="md"
        color="primary"
        class="text-subtitle1"
      />
      <div class="text-subtitle1 agreement__link">
        <a
          href="https://modus-ge.ch/mobilyse-cgu-collaborateur-trice-s"
          target="_blank"
          rel="noopener noreferrer"
          class="text-muted"
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
        size="md"
        color="primary"
        class="text-subtitle1"
      />
      <div class="text-subtitle1 agreement__link">
        <a
          href="https://modus-ge.ch/mobilyse-notice-protection-des-donnees"
          target="_blank"
          class="text-muted"
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

<style scoped lang="scss">
.q-checkbox {
  margin-top: -10px;
  margin-left: -10px;
  margin-bottom: -8px;
}

.agreement__link {
  margin-left: 30px;
}
</style>
