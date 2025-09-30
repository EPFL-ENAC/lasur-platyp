<template>
  <div v-if="hasRecoPro">
    <q-card class="bg-primary">
      <q-card-section>
        <SectionItem :label="t('form.recommendations_pro')" />
        <div
          v-for="(reco, index) in survey.recommendation.reco_pro?.reco_pros"
          :key="index"
          class="rounded-borders q-mb-md bg-secondary text-white"
        >
          <div class="q-pa-md">
            <q-item-label class="text-body1 text-green-6 text-bold">{{
              t('form.journey_pro.label_idx', { index: index + 1 })
            }}</q-item-label>
            <q-item-label class="text-h5">{{ t(`reco.${reco}`) }}</q-item-label>
            <BenefitsPanel :reco="reco" class="q-mt-sm" />
            <q-item-label
              v-if="getActions(index).length"
              class="text-body1 text-green-2 text-bold"
              >{{
                t('form.actions', {
                  count: getActions(index).length,
                  actions: getActions(index).join('; '),
                })
              }}</q-item-label
            >
          </div>
        </div>
      </q-card-section>
      <q-card-section v-if="globalActions.length" class="q-pt-none">
        <div class="text-body1 text-bold text-green-2">
          {{
            t('form.actions_global', {
              count: globalActions.length,
              actions: globalActions.join('; '),
            })
          }}
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import SectionItem from 'src/components/form/SectionItem.vue'
import BenefitsPanel from 'src/components/form/BenefitsPanel.vue'

const { t } = useI18n()
const survey = useSurvey()

const hasRecoPro = computed(
  () =>
    survey.recommendation.reco_pro?.reco_pros &&
    survey.recommendation.reco_pro?.reco_pros.length > 0,
)

function getActions(index: number) {
  const actions = survey.recommendation.reco_actions?.mesure_pro?.[index] || []
  return actions.map(translateAction)
}

const globalActions = computed(() => {
  return survey.recommendation.reco_actions?.mesures_pro_globa?.map(translateAction) || []
})

function translateAction(action: string) {
  const label = t(`actions.${action}`)
  if (label === `actions.${action}`) {
    return action
  }
  return label
}
</script>
