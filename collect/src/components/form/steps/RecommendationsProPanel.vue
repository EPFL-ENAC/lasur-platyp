<template>
  <div v-if="recoPros.length">
    <q-card flat>
      <q-card-section>
        <SectionItem :label="t('form.recommendations_pro')" />
        <q-tabs
          v-model="activeTab"
          dense
          class="text-grey q-mt-md"
          active-color="primary"
          indicator-color="primary"
          align="left"
          narrow-indicator
        >
          <q-tab v-for="(journey, idx) in proJourneys" :key="idx" :name="String(idx)">
            <div class="row items-center no-wrap q-gutter-xs">
              <q-img
                v-if="getModeIcon(journey.mode)?.isSvg"
                :src="getModeIcon(journey.mode)!.icon"
                style="width: 24px; height: 24px"
                no-spinner
                no-transition
                class="icon-primary"
              />
              <q-icon
                v-else
                :name="getModeIcon(journey.mode)?.icon"
                size="sm"
                class="text-primary"
              />
              <span class="text-subtitle2 q-ml-xs">
                {{ t('form.journey_pro.label_idx', { index: idx + 1 }) }}
              </span>
            </div>
          </q-tab>
        </q-tabs>
        <q-tab-panels v-model="activeTab" animated class="bg-transparent">
          <q-tab-panel
            v-for="(journey, idx) in proJourneys"
            :key="idx"
            :name="String(idx)"
            class="full-height"
          >
            <template v-if="recoPros[idx] !== undefined">
              <RecommendationItem
                :reco="recoPros[idx]"
                :reco-label="t(`reco.${recoPros[idx]}`)"
                :actions="getActions(idx)"
                :benefits-expanded="!!benefitsExpanded"
              >
                <PlaceItem
                  v-if="proJourneyLocations[idx]"
                  :map-id="`map-pro-${idx}`"
                  :model-value="proJourneyLocations[idx]"
                  read-only
                  :height="'200px'"
                  class="q-mt-sm q-mb-sm"
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
import RecommendationItem from './RecommendationItem.vue'
import PlaceItem from 'src/components/form/PlaceItem.vue'
import type { PlaceLocation, ProJourney } from 'src/models'
import { getModeIcon } from 'src/utils/modeicons'

const { t } = useI18n()

const props = defineProps<{
  proJourneys: ProJourney[]
  recoPros: string[]
  proJourneyLocations: (PlaceLocation | undefined)[]
  mesurePro: string[][]
  globalActions: string[]
  benefitsExpanded?: boolean
}>()

const activeTab = ref(String(props.proJourneys.length > 0 ? 0 : -1))

function getActions(index: number) {
  return props.mesurePro[index] || []
}
</script>

<style scoped lang="scss">
.icon-primary {
  filter: invert(52%) sepia(88%) saturate(138%) hue-rotate(3deg) brightness(95%) contrast(246%);
}
</style>