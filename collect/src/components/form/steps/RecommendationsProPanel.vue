<template>
  <div v-if="recoPros.length">
    <q-card flat>
      <q-card-section>
        <SectionItem/>
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
                :benefits-expanded="!!benefitsExpanded"
              >
                <PlaceItem
                  v-if="proJourneyLocations[idx]"
                  :map-id="`map-pro-${idx}`"
                  :model-value="proJourneyLocations[idx]"
                  read-only
                  :height="'400px'"
                  class="q-mt-sm q-mb-sm"
                />
              </RecommendationItem>
            </template>
          </q-tab-panel>
        </q-tab-panels>
      </q-card-section>

      <q-card-section
        v-if="hasActions"
        class="q-pt-none employer-measures-section"
      >
        <h6 class="employer-measures-header">{{ t('form.employer_measures_header') }}</h6>
        <p
          v-if="companyName"
          class="employer-measures-description"
        >
          {{ t('form.employer_measures_description', { organisation: companyName }) }}
        </p>

        <div v-if="currentModeActions.length" class="actions-row">
          <div
            v-for="action in currentModeActions"
            :key="action"
            class="action-chip"
          >
            {{ getActionLabel(action) }}
          </div>
        </div>

        <div v-if="globalActions.length" class="actions-row">
          <div
            v-for="action in globalActions"
            :key="action"
            class="action-chip"
          >
            {{ getActionLabel(action) }}
          </div>
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

const getActionLabel = (key: string): string => {
  const label = t(`actions.${key}`)
  return label.startsWith('actions.') ? key : label
}

const props = defineProps<{
  proJourneys: ProJourney[]
  recoPros: string[]
  proJourneyLocations: (PlaceLocation | undefined)[]
  mesurePro: string[][]
  globalActions: string[]
  companyName?: string
  benefitsExpanded?: boolean
}>()

const activeTab = ref(String(props.proJourneys.length > 0 ? 0 : -1))

const currentModeActions = computed<string[]>(() => {
  const idx = parseInt(activeTab.value)
  if (isNaN(idx)) return []
  if (idx < props.mesurePro.length) return props.mesurePro[idx] || []
  return []
})

const hasActions = computed(() => currentModeActions.value.length || props.globalActions.length)
</script>

<style scoped lang="scss">
.icon-primary {
  filter: invert(52%) sepia(88%) saturate(138%) hue-rotate(3deg) brightness(95%) contrast(246%);
}
.employer-measures-header {
  color: $brand-yellow-600;
  font-size: 18px;
  font-weight: 400;
  margin: 8px 0 8px;
}
.employer-measures-description {
  margin: 0 0 12px;
  font-size: 0.95rem;
  color: #4a4a4a;
}
.actions-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}
.action-chip {
  background-color: $brand-yellow-50;
  border: 1px solid #ccc;
  border-radius: 9999px;
  padding: 6px 14px;
  font-size: 0.85rem;
  white-space: nowrap;
}
</style>
