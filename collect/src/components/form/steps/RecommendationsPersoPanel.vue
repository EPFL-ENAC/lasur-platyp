<template>
  <div>
    <q-card flat>
      <q-card-section>
        <q-tabs
          v-if="journeys.length > 1"
          v-model="activeTab"
          dense
          no-caps
          active-color="primary"
          indicator-color="primary"
          align="left"
          narrow-indicator
        >
          <q-tab v-for="(_, idx) in journeys" :key="idx" :name="String(idx)">
            <div class="row items-center no-wrap q-gutter-xs">
              <template v-for="(mode, mIdx) in journeys[idx]?.modes" :key="mIdx">
                <q-img
                  v-if="getModeIcon(mode)?.isSvg"
                  :src="getModeIcon(mode)!.icon"
                  style="width: 24px; height: 24px"
                  no-spinner
                  no-transition
                  class="icon-primary"
                />
                <q-icon v-else :name="getModeIcon(mode)?.icon" size="sm" class="text-primary" />
              </template>
              <span class="text-subtitle2 q-ml-xs">
                {{ t('form.journey.label_idx', { index: idx + 1 }) }}
              </span>
            </div>
          </q-tab>
        </q-tabs>

        <!-- Sits with the journey it describes: under the tabs, above the mode. -->
        <BravoBanner
          v-if="activeBravo > 0 && activeReco"
          :bravo="activeBravo"
          :reco="activeReco"
          :benefits-expanded="!!benefitsExpanded"
          class="q-mb-lg"
        />
        <q-tab-panels v-model="activeTab" animated class="bg-transparent">
          <q-tab-panel
            v-for="(_, idx) in journeys"
            :key="idx"
            :name="String(idx)"
            class="full-height q-pa-none"
          >
            <template v-if="recoInter[idx] !== undefined">
              <RecommendationItem
                :reco="recoInter[idx]"
                :reco-label="t(`reco.${recoInter[idx]}`)"
                :bravo="bravo[idx]"
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
    </q-card>

    <!-- Its own block on the page rather than a footer inside the journey card. -->
    <section v-if="measureActions.length" class="employer-measures">
      <div class="employer-measures__eyebrow question-hint">
        {{ t('form.employer_measures_eyebrow') }}
      </div>
      <h3 class="employer-measures__header">{{ t('form.employer_measures_header') }}</h3>
      <p class="employer-measures__description question-hint">
        {{ t('form.employer_measures_description', { organisation: companyName }) }}
      </p>

      <div class="row q-col-gutter-md">
        <div v-for="action in measureActions" :key="action" class="col-12 col-md-6">
          <ContentCard>
            <div class="row items-start no-wrap">
              <q-icon name="redeem" size="sm" class="employer-measures__icon q-mr-md" />
              <div class="question-label text-bold">{{ getActionLabel(action) }}</div>
            </div>
          </ContentCard>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import ContentCard from '@/components/form/ContentCard.vue'
import IsochronesMap from '@/components/form/IsochronesMap.vue'
import RecommendationItem from './RecommendationItem.vue'
import BravoBanner from './BravoBanner.vue'
import type { Journey } from '@/models'
import { getModeIcon } from '@/utils/modeicons'

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
  companyName: string
  benefitsExpanded?: boolean
}>()

const activeTab = ref(String(props.journeys.length > 0 ? 0 : -1))

// The banner sits above the card, so it follows whichever journey is on show.
const activeIndex = computed(() => parseInt(activeTab.value))
const activeBravo = computed(() => props.bravo[activeIndex.value] ?? 0)
const activeReco = computed(() => props.recoInter[activeIndex.value] ?? '')

const currentModeActions = computed(() => {
  const idx = parseInt(activeTab.value)
  if (isNaN(idx)) return []
  if (idx === 0) return props.mesureDt1
  if (idx === 1) return props.mesureDt2
  return []
})

// One list for the grid: the measures tied to the selected journey, then the
// ones the employer offers regardless of mode.
const measureActions = computed(() => [...currentModeActions.value, ...props.globalActions])

function showIsochrones(reco: string) {
  return ['marche', 'velo', 'vae', 'cargo', 'train', 'tpu'].includes(reco)
}

function zoomIsochrones(reco: string) {
  return reco === 'marche' ? 11 : 9
}
</script>

<style scoped lang="scss">
.icon-primary {
  filter: invert(52%) sepia(88%) saturate(138%) hue-rotate(3deg) brightness(95%) contrast(246%);
}
.employer-measures {
  margin-top: 48px;
}

.employer-measures__eyebrow {
  margin-bottom: 4px;
  color: var(--hint-color);
}

.employer-measures__header {
  margin: 0 0 8px;
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 2rem;
}

.employer-measures__description {
  margin: 0 0 24px;
}

// Icon sits in the same bordered square as the rest of the design system.
.employer-measures__icon {
  flex-shrink: 0;
  padding: 8px;
  border: 1px solid var(--secondary-border-color);
  border-radius: $button-border-radius;
}
</style>
