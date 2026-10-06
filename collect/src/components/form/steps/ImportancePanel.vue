<template>
  <!-- One box per entry, paired left/right so the stars line up row by row. -->
  <div class="row q-col-gutter-lg rating-grid step-content">
    <div class="col-12 col-md-6">
      <ContentCard>
        <RatingItem
          :label="t('form.importance_time')"
          v-model="survey.record.data.importance_time"
          :max="5"
        />
      </ContentCard>
    </div>
    <div class="col-12 col-md-6">
      <ContentCard>
        <RatingItem
          :label="t('form.importance_comfort')"
          v-model="survey.record.data.importance_comfort"
          :max="5"
        />
      </ContentCard>
    </div>
    <div class="col-12 col-md-6">
      <ContentCard>
        <RatingItem
          :label="t('form.importance_cost')"
          v-model="survey.record.data.importance_cost"
          :max="5"
        />
      </ContentCard>
    </div>
    <div class="col-12 col-md-6">
      <ContentCard>
        <RatingItem
          :label="t('form.importance_most')"
          v-model="survey.record.data.importance_most"
          :max="5"
        />
      </ContentCard>
    </div>
    <div class="col-12 col-md-6">
      <ContentCard>
        <RatingItem
          :label="t('form.importance_flex')"
          v-model="survey.record.data.importance_flex"
          :max="5"
        />
      </ContentCard>
    </div>
    <div class="col-12 col-md-6">
      <ContentCard>
        <RatingItem
          :label="t('form.importance_env')"
          v-model="survey.record.data.importance_env"
          :max="5"
        />
      </ContentCard>
    </div>
    <div class="col-12 col-md-6">
      <ContentCard>
        <RatingItem
          :label="t('form.importance_rel')"
          v-model="survey.record.data.importance_rel"
          :max="5"
        />
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
