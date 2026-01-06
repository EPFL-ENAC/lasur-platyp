<template>
  <div>
    <SectionItem :label="t('form.change')" label-class="text-h4" class="q-mb-md" />
    <q-card class="bg-primary q-mb-xl">
      <q-card-section class="q-pa-sm">
        <div class="text-h5 text-center">
          {{ t(`reco.${firstRecoDt}`) }}
        </div>
      </q-card-section>
    </q-card>
    <RatingItem
      v-if="isRecoChange"
      :label="t('form.change_motivation')"
      :hint="t('form.change_motivation_hint')"
      v-model="survey.record.data.change.motivation"
      :max="5"
      label-class="text-h5"
      class="q-mb-lg"
      @update:model-value="onSave"
    />
    <ChoiceItem
      :label="t('form.change_levers')"
      :options="[
        { value: 'finance', label: t('form.change_levers_option.financial_support') },
        { value: 'flexibility', label: t('form.change_levers_option.work_flexibility') },
        { value: 'collective', label: t('form.change_levers_option.collective_changes') },
        { value: 'environment', label: t('form.change_levers_option.work_environment') },
        { value: 'other', label: t('form.change_levers_option.other') },
      ]"
      v-model="survey.record.data.change.levers"
      multiple
      label-class="text-h5"
      option-label-class="text-h5"
      @update:model-value="onSave"
    />
    <q-input
      v-if="survey.record.data.change.levers?.includes('other')"
      v-model="survey.record.data.change.other_levers"
      :label="t('form.change_other_levers_specify')"
      type="textarea"
      class="q-mb-lg text-h6"
      bg-color="green-3"
      filled
      debounce="500"
      @update:model-value="onSave"
    />
  </div>
</template>

<script setup lang="ts">
import SectionItem from 'src/components/form/SectionItem.vue'
import RatingItem from 'src/components/form/RatingItem.vue'
import ChoiceItem from 'src/components/form/ChoiceItem.vue'

const { t } = useI18n()
const survey = useSurvey()

const emit = defineEmits(['update:modelValue'])

const isRecoChange = computed(() => !survey.isRecommendationInUse())

const firstRecoDt = computed(() =>
  survey.recommendation.reco && survey.recommendation.reco.reco_dt2.length
    ? survey.recommendation.reco.reco_dt2[0]
    : '',
)

function onSave() {
  emit('update:modelValue')
}
</script>
