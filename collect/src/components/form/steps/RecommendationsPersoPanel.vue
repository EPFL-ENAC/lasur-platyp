<template>
  <div>
    <div class="q-mb-lg">
      <div class="text-h5 text-bold q-mb-md">{{ t(`main_mode.${mainFm}`) }}</div>
    </div>

    <q-card flat>
      <q-card-section>
        <div class="text-h5">
          <SectionItem :label="sectionLabel" />
        </div>

        <template v-for="(reco, idx) in recoDt" :key="idx">
          <q-separator />
          <RecommendationItem
            :reco="reco"
            :reco-label="t(`reco.${reco}`)"
            :index-label="
              t(
                isModeSustainable && isModeOptions
                  ? 'form.journey.label_option_idx'
                  : 'form.journey.label_idx',
                { index: idx + 1 },
              )
            "
            :actions="getActions(idx)"
            :benefits-expanded="!!benefitsExpanded"
          >
            <IsochronesMap
              v-if="showIsochrones(reco) && center"
              :center="center"
              :reco="reco"
              :height="'400px'"
              :zoom="zoomIsochrones(reco)"
              class="q-mt-sm"
            />
          </RecommendationItem>
        </template>
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
import IsochronesMap from 'src/components/form/IsochronesMap.vue'
import RecommendationItem from './RecommendationItem.vue'

const { t } = useI18n()

const props = defineProps<{
  mainFm: string
  isModeSustainable: boolean
  isModeOptions: boolean
  recoDt: string[]
  center: [number, number] | null
  mesureDt1: string[]
  mesureDt2: string[]
  globalActions: string[]
  benefitsExpanded?: boolean
}>()

const sectionLabel = computed(() => {
  if (props.isModeSustainable && !props.isModeOptions) {
    return t('main_mode.sustainable')
  }
  if (props.isModeSustainable && props.isModeOptions) {
    return t('main_mode.sustainable_options')
  }
  return t('main_mode.not_sustainable')
})

function showIsochrones(reco: string) {
  return ['marche', 'velo', 'vae', 'cargo', 'train', 'tpu'].includes(reco)
}

function zoomIsochrones(reco: string) {
  return reco === 'marche' ? 11 : 9
}

function getActions(idx: number) {
  if (idx === 0) return props.mesureDt1
  if (idx === 1) return props.mesureDt2
  return []
}
</script>
