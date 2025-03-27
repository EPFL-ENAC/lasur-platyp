<template>
  <div>
    <div class="q-mb-lg">
      <div class="text-h5 text-bold q-mb-md">
        {{ t(`main_mode.${mainFm}`) }}
      </div>
    </div>
    <q-card class="bg-primary">
      <q-card-section>
        <div class="text-h5">
          <SectionItem
            v-if="['car', 'moto'].includes(mainFm)"
            :label="t(`main_mode.not_sustainable`)"
          />
          <SectionItem v-else :label="t(`main_mode.sustainable`)" />
        </div>
        <q-list>
          <template v-for="(reco, idx) in recoDt" :key="idx">
            <q-item
              active-class="bg-teal-1 text-grey-8"
              v-ripple
              clickable
              class="rounded-borders q-mb-md bg-secondary text-white"
            >
              <q-item-section>
                <q-item-label class="text-h5">{{ t(`reco.${reco}`) }}</q-item-label>
                <q-item-label
                  v-if="getActions(idx).length"
                  class="text-body1 text-green-2 text-bold"
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
      </q-card-section>
      <q-card-section v-if="globalActions.length" class="q-pt-none">
        <div class="text-body1 text-bold text-green-2">
          {{
            t('form.actions_global', {
              count: globalActions.length,
              actions: globalActions.join(', '),
            })
          }}
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import SectionItem from 'src/components/form/SectionItem.vue'

const { t } = useI18n()
const survey = useSurvey()

const mainFm = computed(() => {
  const data = survey.record.data
  if (data.freq_mod_combined) return 'combined'
  const fm: { [key: string]: number } = {
    walking: data.freq_mod_walking,
    bike: data.freq_mod_bike,
    pub: data.freq_mod_pub,
    moto: data.freq_mod_moto,
    car: data.freq_mod_car,
    train: data.freq_mod_train,
  }
  let max = -1
  let main = ''
  Object.keys(fm).forEach((key) => {
    if (fm[key] !== undefined && fm[key] > max) {
      max = fm[key]
      main = key
    }
  })
  return main
})

const recoDt = computed(() =>
  survey.recommendation.reco ? survey.recommendation.reco.reco_dt2 : [],
)

const mesure_dt1 = computed(() => survey.recommendation.reco_actions?.mesure_dt1 || [])
const mesure_dt2 = computed(() => survey.recommendation.reco_actions?.mesure_dt2 || [])
// const hasActions = computed(() => mesure_dt1.value.length > 0 || mesure_dt2.value.length > 0)

function getActions(idx: number) {
  if (idx === 0) {
    return mesure_dt1.value.map((action) => t(`actions.${action}`)) || []
  } else if (idx === 1) {
    return mesure_dt2.value.map((action) => t(`actions.${action}`)) || []
  }
  return []
}

const globalActions = computed(() => {
  return (
    survey.recommendation.reco_actions?.mesures_globa?.map((action: string) =>
      t(`actions.${action}`),
    ) || []
  )
})
</script>
