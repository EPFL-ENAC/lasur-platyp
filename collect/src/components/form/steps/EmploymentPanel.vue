<template>
  <q-card flat>
    <q-card-section>
      <NumberItem
        :label="t('form.employment_rate')"
        label-class="text-h5 q-mb-md"
        v-model="survey.record.data.employment_rate"
        :min="0"
        :max="100"
        :step="5"
        unit="%"
        class="q-mb-xl"
      />
      <NumberItem
        :label="t('form.remote_work_rate')"
        label-class="text-h5 q-mb-md"
        v-model="survey.record.data.remote_work_rate"
        :min="0"
        :max="100"
        :step="5"
        unit="%"
        class="q-mb-xl"
      />
      <ToggleItem
        :label="t('form.company_vehicle')"
        label-class="text-h5"
        :left-label="t('form.no')"
        :right-label="t('form.yes')"
        v-model="survey.record.data.company_vehicle"
        required
        class="q-mb-lg"
      />
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import NumberItem from 'src/components/form/NumberItem.vue'
import ToggleItem from 'src/components/form/ToggleItem.vue'

const { t } = useI18n()
const survey = useSurvey()
</script>
