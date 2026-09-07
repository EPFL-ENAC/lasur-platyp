<template>
  <div>
    <ContentCard>
      <NumberItem
        :label="t('form.employment_rate')"
        label-class="question-label text-bold q-mb-md"
        v-model="survey.record.data.employment_rate"
        :min="0"
        :max="100"
        :step="5"
        unit="%"
      />
    </ContentCard>
    <ContentCard>
      <NumberItem
        :label="t('form.remote_work_rate')"
        label-class="question-label text-bold q-mb-md"
        v-model="survey.record.data.remote_work_rate"
        :min="0"
        :max="100"
        :step="5"
        unit="%"
      />
    </ContentCard>
    <ContentCard>
      <ToggleItem
        :label="t('form.company_vehicle')"
        label-class="question-label text-bold"
        :true-label="t('form.yes')"
        :false-label="t('form.no')"
        v-model="survey.record.data.company_vehicle"
      />
    </ContentCard>
  </div>
</template>

<script setup lang="ts">
import NumberItem from '@/components/form/NumberItem.vue'
import ToggleItem from '@/components/form/ToggleItem.vue'
import ContentCard from '@/components/form/ContentCard.vue'

const { t } = useI18n()
const survey = useSurvey()
</script>
