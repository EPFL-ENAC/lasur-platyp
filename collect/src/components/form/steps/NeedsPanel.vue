<template>
  <div class="row">
    <div class="col-sm-12 col-md-6">
      <RatingItem
        :label="t('form.mode.walking')"
        v-model="survey.record.data.needs_walking"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <RatingItem
        :label="t('form.mode.bike')"
        v-model="survey.record.data.needs_bike"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <RatingItem
        :label="t('form.mode.pub')"
        v-model="survey.record.data.needs_pub"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
    </div>
    <div class="col-sm-12 col-md-6">
      <RatingItem
        :label="t('form.mode.train')"
        v-model="survey.record.data.needs_train"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <RatingItem
        :label="t('form.mode.moto')"
        v-model="survey.record.data.needs_moto"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <RatingItem
        :label="t('form.mode.car')"
        v-model="survey.record.data.needs_car"
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
