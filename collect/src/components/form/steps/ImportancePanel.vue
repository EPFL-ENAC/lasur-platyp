<template>
  <div class="row">
    <div class="col-sm-12 col-md-6">
      <RatingItem
        :label="t('form.importance_time')"
        v-model="survey.record.data.importance_time"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <RatingItem
        :label="t('form.importance_cost')"
        v-model="survey.record.data.importance_cost"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <RatingItem
        :label="t('form.importance_flex')"
        v-model="survey.record.data.importance_flex"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <RatingItem
        :label="t('form.importance_rel')"
        v-model="survey.record.data.importance_rel"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
    </div>
    <div class="col-sm-12 col-md-6">
      <RatingItem
        :label="t('form.importance_comfort')"
        v-model="survey.record.data.importance_comfort"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <RatingItem
        :label="t('form.importance_most')"
        v-model="survey.record.data.importance_most"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <RatingItem
        :label="t('form.importance_env')"
        v-model="survey.record.data.importance_env"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import RatingItem from 'src/components/form/RatingItem.vue'
const { t } = useI18n()
const survey = useSurvey()
</script>
