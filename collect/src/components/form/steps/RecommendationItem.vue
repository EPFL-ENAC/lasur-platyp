<template>
  <div :class="wrapperClass">
    <div class="q-pa-md">
      <q-item-label v-if="indexLabel" class="text-body1 text-primary text-bold">
        {{ indexLabel }}
      </q-item-label>
      <div v-if="bravo !== undefined && bravo > 0" class="bravo-box">
        <div class="bravo-text">
          {{ t(`bravo.${bravo}`) }}
        </div>
        <div v-if="hasBenefits(reco) && !benefitsExpanded" class="bravo-btn-wrapper">
          <q-btn
            class="benefits-btn"
            size="md"
            no-caps
            dense
          >
            <q-icon name="workspace_premium" class="q-mr-xs" />
            {{ t('benefits.show') }}
            <q-menu class="q-mr-md bg-white text-secondary rounded-borders q-pa-md" :max-width="'400px'">
              <q-markdown :src="getBenefits(reco, locale)" />
            </q-menu>
          </q-btn>
        </div>
      </div>
      <template v-if="bravo !== 2">
        <div v-if="bravo === 0" class="bravo-box">
          <div class="reco-intro">
            {{ t('bravo.recommends') }}
          </div>
          <div v-if="hasBenefits(reco) && !benefitsExpanded" class="bravo-btn-wrapper">
            <q-btn
              class="benefits-btn"
              size="md"
              no-caps
              dense
            >
              <q-icon name="workspace_premium" class="q-mr-xs" />
              {{ t('benefits.show') }}
              <q-menu class="q-mr-md bg-white text-secondary rounded-borders q-pa-md" :max-width="'400px'">
                <q-markdown :src="getBenefits(reco, locale)" />
              </q-menu>
            </q-btn>
          </div>
        </div>
        <div v-if="bravo !== undefined && bravo > 0" class="reco-intro">
          {{ t('bravo.recommends_also') }}
        </div>
        <q-item-label :class="recoClass || 'text-h5'">
          {{ recoLabel }}
        </q-item-label>
        <BenefitsPanel v-if="!hasBenefits(reco) || benefitsExpanded" :reco="reco" class="q-mt-sm" :expanded="!!benefitsExpanded" />
      </template>
      <slot />
      <q-item-label v-if="actions?.length" class="text-body1 text-green-2 text-bold q-mt-md">
        {{
          t('form.actions', {
            count: actions.length,
            actions: actions.map(getActionLabel).join('; '),
          })
        }}
      </q-item-label>
    </div>
  </div>
</template>
<script setup lang="ts">
import BenefitsPanel from 'src/components/form/steps/BenefitsPanel.vue'
import { hasBenefits, getBenefits } from 'src/utils/benefits'
const { locale, t } = useI18n()

const getActionLabel = (key: string): string => {
  const label = t(`actions.${key}`)
  return label.startsWith('actions.') ? key : label
}
withDefaults(
  defineProps<{
    reco: string
    recoLabel: string
    bravo: number | undefined
    indexLabel?: string
    recoClass?: string
    wrapperClass?: string
    actions?: string[]
    benefitsExpanded?: boolean
  }>(),
  {
    recoClass: 'text-h5',
    wrapperClass: '',
    benefitsExpanded: false,
    actions: () => [],
  },
)
</script>
<style scoped>
.bravo-box {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  color: #168654;
  background-color: #f5fbf9;
  border: 1px solid #cedfd7;
  border-radius: 8px;
  padding: 8px 16px;
  margin-bottom: 16px;
  font-size: 16px;
}
.bravo-text {
  flex: 1;
}
.bravo-btn-wrapper {
  flex-shrink: 0;
  margin-left: 16px;
}
.reco-intro {
  color: #168654;
  margin-bottom: 8px;
  font-size: 16px;
}
.benefits-btn {
  background-color: #168654 !important;
  color: white !important;
}
</style>
