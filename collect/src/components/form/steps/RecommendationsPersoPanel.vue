<template>
  <div>
    <q-card flat>
      <q-card-section>
        <SectionItem :label="t('form.recommendations')" />
        <q-tabs
          v-model="activeTab"
          dense
          class="text-grey q-mt-md"
          active-color="primary"
          indicator-color="primary"
          align="left"
          narrow-indicator
        >
          <q-tab v-for="(_, idx) in journeys" :key="idx" :name="String(idx)">
            <div class="row items-center no-wrap q-gutter-xs">
              <template v-for="(mode, mIdx) in journeys[idx].modes" :key="mIdx">
                <q-img
                  v-if="getModeIcon(mode)?.isSvg"
                  :src="getModeIcon(mode)!.icon"
                  style="width: 24px; height: 24px"
                  no-spinner
                  no-transition
                  class="icon-primary"
                />
                <q-icon
                  v-else
                  :name="getModeIcon(mode)?.icon"
                  size="sm"
                  class="text-primary"
                />
              </template>
              <span class="text-subtitle2 q-ml-xs">
                {{ t('form.journey.label_idx', { index: idx + 1 }) }}
              </span>
            </div>
          </q-tab>
        </q-tabs>
        <q-tab-panels v-model="activeTab" animated class="bg-transparent">
          <q-tab-panel
            v-for="(_, idx) in journeys"
            :key="idx"
            :name="String(idx)"
            class="full-height"
          >
            <template v-if="recoInter[idx] !== undefined">
              <RecommendationItem
                :reco="recoInter[idx]"
                :reco-label="t(`reco.${recoInter[idx]}`)"
                :bravo="bravo[idx]"
                :actions="getActions(idx)"
                :benefits-expanded="!!benefitsExpanded"
              >
                <IsochronesMap
                  v-if="showIsochrones(recoInter[idx]) && center"
                  :center="center"
                  :reco="recoInter[idx]"
                  :height="'400px'"
                  :zoom="zoomIsochrones(recoInter[idx])"
                  class="q-mt-sm"
                />
              </RecommendationItem>
            </template>
          </q-tab-panel>
        </q-tab-panels>
      </q-card-section>

      <q-card-section v-if="globalActions.length" class="q-pt-none">
        <div class="text-body1 text-bold text-green-2">
          {{
            t('form.actions_global', {
              count: globalActions.length,
              actions: globalActions.map(getActionLabel).join('; '),
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
import type { Journey } from 'src/models'
import { getModeIcon } from 'src/utils/modeicons'

const { t } = useI18n()

const getActionLabel = (key: string): string => {
  const label = t(`actions.${key}`)
  return label.startsWith('actions.') ? key : label
}

const props = defineProps<{
  journeys: Journey[]
  recoInter: string[]
  bravo: number[]
  center: [number, number] | null
  mesureDt1: string[]
  mesureDt2: string[]
  globalActions: string[]
  benefitsExpanded?: boolean
}>()

const activeTab = ref(String(props.journeys.length > 0 ? 0 : -1))

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

<style scoped lang="scss">
.icon-primary {
  filter: invert(52%) sepia(88%) saturate(138%) hue-rotate(3deg) brightness(95%) contrast(246%);
}
</style>