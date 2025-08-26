<template>
  <div v-if="hasRecoPro">
    <q-card class="bg-primary">
      <q-card-section>
        <SectionItem :label="t('form.recommendations_pro')" />
        <div v-if="recoLoc" class="rounded-borders q-mb-md bg-secondary text-white">
          <div class="q-pa-md">
            <q-item-label class="text-body1 text-green-6 text-bold">{{ t('local') }}</q-item-label>
            <q-item-label class="text-h5">{{ t(`reco.${recoLoc}`) }}</q-item-label>
            <BenefitsPanel :reco="recoLoc" />
            <q-item-label v-if="actionsLoc.length" class="text-body1 text-green-2 text-bold">{{
              t('form.actions', {
                count: actionsLoc.length,
                actions: actionsLoc.join('; '),
              })
            }}</q-item-label>
          </div>
        </div>
        <div v-if="recoReg" class="rounded-borders q-mb-md bg-secondary text-white">
          <div class="q-pa-md">
            <q-item-label class="text-body1 text-green-6 text-bold">{{
              t('regional')
            }}</q-item-label>
            <q-item-label class="text-h5">{{ t(`reco.${recoReg}`) }}</q-item-label>
            <BenefitsPanel :reco="recoReg" />
            <q-item-label v-if="actionsRegInt.length" class="text-body1 text-green-2 text-bold">{{
              t('form.actions', {
                count: actionsRegInt.length,
                actions: actionsRegInt.join('; '),
              })
            }}</q-item-label>
          </div>
        </div>
        <div v-if="recoInt" class="rounded-borders q-mb-md bg-secondary text-white">
          <div class="q-pa-md">
            <q-item-label class="text-body1 text-green-6 text-bold">{{
              t('international')
            }}</q-item-label>
            <q-item-label class="text-h5">{{ t(`reco.${recoInt}`) }}</q-item-label>
            <BenefitsPanel :reco="recoInt" />
            <q-item-label v-if="actionsRegInt.length" class="text-body1 text-green-2 text-bold">{{
              t('form.actions', {
                count: actionsRegInt.length,
                actions: actionsRegInt.join('; '),
              })
            }}</q-item-label>
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
    survey.recommendation.reco_pro &&
    (survey.recommendation.reco_pro.reco_pro_loc !== '' ||
      survey.recommendation.reco_pro.reco_pro_reg !== '' ||
      survey.recommendation.reco_pro.reco_pro_int !== ''),
)

const recoLoc = computed(() => survey.recommendation.reco_pro?.reco_pro_loc || '')
const recoReg = computed(() => survey.recommendation.reco_pro?.reco_pro_reg || '')
const recoInt = computed(() => survey.recommendation.reco_pro?.reco_pro_int || '')

const actionsLoc = computed(
  () => survey.recommendation.reco_actions?.mesure_pro_loc.map(translateAction) || [],
)
const actionsRegInt = computed(
  () => survey.recommendation.reco_actions?.mesure_pro_regint.map(translateAction) || [],
)

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
