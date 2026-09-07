<template>
  <div :class="wrapperClass">
    <div class="q-pa-none">
      <q-item-label v-if="indexLabel" class="text-body1 text-primary text-bold">
        {{ indexLabel }}
      </q-item-label>

      <template v-if="bravo !== 2">
        <div v-if="bravo !== undefined && bravo > 0" class="reco-intro">
          {{ t('bravo.recommends_also') }}
        </div>

        <div v-if="bravo === 0" class="reco-intro">
          {{ t('bravo.recommends') }}
        </div>

        <div class="reco-label-row">
          <q-item-label :class="recoClass || 'reco-label'" class="reco-label-item">
            <q-icon :name="getRecoIcon(reco)" size="sm" class="reco-label__icon q-mr-sm" />
            {{ recoLabel }}
          </q-item-label>
        </div>

        <BenefitsPanel
          v-if="!hasBenefits(reco) || benefitsExpanded"
          :reco="reco"
          class="q-mt-sm"
          :expanded="!!benefitsExpanded"
        />
      </template>

      <slot />

      <q-item-label v-if="actions?.length" class="text-body1 text-green-2 text-bold q-mt-md">
        {{
          t('form.actions', {
            count: actions.length,
            actions: actions.join('; '),
          })
        }}
      </q-item-label>
    </div>
  </div>
</template>

<script setup lang="ts">
import BenefitsPanel from '@/components/form/steps/BenefitsPanel.vue'
import { hasBenefits } from '@/utils/benefits'
import { getRecoIcon } from '@/utils/modeicons'

const { t } = useI18n()

withDefaults(
  defineProps<{
    reco: string
    recoLabel: string
    bravo?: number | undefined
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

<style scoped lang="scss">
.reco-intro {
  color: var(--title-color);
  font-size: 1rem;
  margin-bottom: 8px;
}

.reco-label {
  display: flex;
  align-items: center;
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 2rem;
}

.reco-label__icon {
  color: $primary;
}

.reco-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.reco-label-item {
  flex: 1;
}
</style>
