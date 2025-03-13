<template>
  <div v-if="hasRecoPro">
    <SectionItem :label="t('form.recommendations_pro')" />
    <q-list>
      <q-item
        v-if="recoLoc"
        active-class="bg-teal-1 text-grey-8"
        v-ripple
        clickable
        class="rounded-borders q-mb-md bg-primary text-white"
      >
        <q-item-section>
          <q-item-label class="text-body1 text-green-3 text-bold">{{ t('local') }}</q-item-label>
          <q-item-label class="text-h5">{{ t(`reco.${recoLoc}`) }}</q-item-label>
          <q-item-label v-if="actionsLoc.length" class="text-body1 text-green-10 text-bold">{{
            t('form.actions', {
              count: actionsLoc.length,
              actions: actionsLoc.join(', '),
            })
          }}</q-item-label>
        </q-item-section>
      </q-item>
      <q-item
        v-if="recoReg"
        active-class="bg-teal-1 text-grey-8"
        v-ripple
        clickable
        class="rounded-borders q-mb-md bg-primary text-white"
      >
        <q-item-section>
          <q-item-label class="text-body1 text-green-3 text-bold">{{ t('regional') }}</q-item-label>
          <q-item-label class="text-h5">{{ t(`reco.${recoReg}`) }}</q-item-label>
          <q-item-label v-if="actionsRegInt.length" class="text-body1 text-green-10 text-bold">{{
            t('form.actions', {
              count: actionsRegInt.length,
              actions: actionsRegInt.join(', '),
            })
          }}</q-item-label>
        </q-item-section>
      </q-item>
      <q-item
        v-if="recoInt"
        active-class="bg-teal-1 text-grey-8"
        v-ripple
        clickable
        class="rounded-borders q-mb-md bg-primary text-white"
      >
        <q-item-section>
          <q-item-label class="text-body1 text-green-3 text-bold">{{
            t('international')
          }}</q-item-label>
          <q-item-label class="text-h5">{{ t(`reco.${recoInt}`) }}</q-item-label>
          <q-item-label v-if="actionsRegInt.length" class="text-body1 text-green-10 text-bold">{{
            t('form.actions', {
              count: actionsRegInt.length,
              actions: actionsRegInt.join(', '),
            })
          }}</q-item-label>
        </q-item-section>
      </q-item>
    </q-list>
  </div>
</template>

<script setup lang="ts">
import SectionItem from 'src/components/form/SectionItem.vue'

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
  () =>
    survey.recommendation.reco_actions?.mesure_pro_loc.map((action) => t(`actions.${action}`)) ||
    [],
)
const actionsRegInt = computed(
  () =>
    survey.recommendation.reco_actions?.mesure_pro_regint.map((action) => t(`actions.${action}`)) ||
    [],
)
</script>
