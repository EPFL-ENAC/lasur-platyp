<template>
  <div>
    <SectionItem :label="t('form.recommendations')" />
    <q-list>
      <template v-for="(reco, idx) in recoDt" :key="idx">
        <q-item
          active-class="bg-teal-1 text-grey-8"
          v-ripple
          clickable
          class="rounded-borders q-mb-md bg-primary text-white"
        >
          <q-item-section>
            <q-item-label class="text-h5">{{ t(`reco.${reco}`) }}</q-item-label>
            <q-item-label
              v-if="getActions(idx).length"
              class="text-body1 text-green-10 text-bold"
              >{{
                t('form.actions', {
                  count: getActions(idx).length,
                  actions: getActions(idx).join(', '),
                })
              }}</q-item-label
            >
          </q-item-section>
        </q-item>
      </template>
    </q-list>
  </div>
</template>

<script setup lang="ts">
import SectionItem from 'src/components/form/SectionItem.vue'

const { t } = useI18n()
const survey = useSurvey()

const recoDt = computed(() =>
  survey.recommendation.reco ? survey.recommendation.reco.reco_dt2 : [],
)

function getActions(idx: number) {
  if (idx === 0) {
    return (
      survey.recommendation.reco_actions?.mesure_dt1.map((action) => t(`actions.${action}`)) || []
    )
  } else if (idx === 1) {
    return (
      survey.recommendation.reco_actions?.mesure_dt2.map((action) => t(`actions.${action}`)) || []
    )
  }
  return []
}
</script>
