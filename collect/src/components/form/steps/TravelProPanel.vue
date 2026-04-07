<template>
  <q-card flat>
    <q-card-section>
      <ToggleItem
        v-model="survey.record.data.travel_pro"
        required
        :label="t('form.travel_pro')"
        label-class="text-h5"
        :left-label="t('form.no')"
        :right-label="t('form.yes')"
      />
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import ToggleItem from 'src/components/form/ToggleItem.vue'

const { t } = useI18n()
const survey = useSurvey()
</script>
