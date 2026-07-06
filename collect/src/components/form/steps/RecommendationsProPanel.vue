<template>
  <div v-if="recoPros.length">
    <q-card flat>
      <q-card-section>
        <SectionItem :label="t('form.recommendations_pro')" />

        <template v-for="(reco, index) in recoPros" :key="index">
          <q-separator />
          <RecommendationItem
            :reco="reco"
            :reco-label="t(`reco.${reco}`)"
            :index-label="t('form.journey_pro.label_idx', { index: index + 1 })"
            :reco-class="reco === 'avoid' ? 'text-subtitle1' : 'text-h5'"
            wrapper-class="rounded-borders q-mb-md bg-secondary text-white"
            :actions="getActions(index)"
            :benefits-expanded="!!benefitsExpanded"
          >
            <PlaceItem
              v-if="proJourneyLocations[index]"
              :map-id="`map-pro-${index}`"
              :model-value="proJourneyLocations[index]"
              read-only
              :height="'200px'"
              class="q-mt-sm q-mb-sm"
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
import RecommendationItem from './RecommendationItem.vue'
import PlaceItem from 'src/components/form/PlaceItem.vue'
import type { PlaceLocation } from 'src/models'

const { t } = useI18n()

const props = defineProps<{
  recoPros: string[]
  proJourneyLocations: (PlaceLocation | undefined)[]
  mesurePro: string[][]
  globalActions: string[]
  benefitsExpanded?: boolean
}>()

function getActions(index: number) {
  return props.mesurePro[index] || []
}
</script>