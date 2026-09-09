<template>
  <!-- One box per entry, paired left/right so the stars line up row by row. -->
  <div class="row q-col-gutter-lg rating-grid step-content">
    <div class="col-12 col-md-6">
      <ContentCard>
        <RatingItem
          :label="t('form.mode.walking')"
          v-model="survey.record.data.needs_walking"
          :max="5"
        />
      </ContentCard>
    </div>
    <div class="col-12 col-md-6">
      <ContentCard>
        <RatingItem
          :label="t('form.mode.train')"
          v-model="survey.record.data.needs_train"
          :max="5"
        />
      </ContentCard>
    </div>
    <div class="col-12 col-md-6">
      <ContentCard>
        <RatingItem :label="t('form.mode.bike')" v-model="survey.record.data.needs_bike" :max="5" />
      </ContentCard>
    </div>
    <div class="col-12 col-md-6">
      <ContentCard>
        <RatingItem :label="t('form.mode.moto')" v-model="survey.record.data.needs_moto" :max="5" />
      </ContentCard>
    </div>
    <div class="col-12 col-md-6">
      <ContentCard>
        <RatingItem :label="t('form.mode.pub')" v-model="survey.record.data.needs_pub" :max="5" />
      </ContentCard>
    </div>
    <div class="col-12 col-md-6">
      <ContentCard>
        <RatingItem :label="t('form.mode.car')" v-model="survey.record.data.needs_car" :max="5" />
      </ContentCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import RatingItem from '@/components/form/RatingItem.vue'
import ContentCard from '@/components/form/ContentCard.vue'

const { t } = useI18n()
const survey = useSurvey()
</script>
