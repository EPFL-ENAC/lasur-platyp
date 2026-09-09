<template>
  <div class="bravo-box">
    <q-icon name="verified" size="sm" class="bravo-box__icon q-mr-md" />
    <div class="bravo-box__text">
      {{ t(`bravo.${bravo}`) }}
    </div>
    <div v-if="hasBenefits(reco) && !benefitsExpanded" class="bravo-box__action">
      <q-btn class="bravo-box__btn" size="md" no-caps dense>
        <q-icon name="workspace_premium" class="q-mr-xs" />
        {{ t('benefits.show') }}
        <q-menu
          class="q-mr-md bg-white text-secondary rounded-borders q-pa-md"
          :max-width="'400px'"
          anchor="top end"
          self="top start"
        >
          <q-markdown :src="getBenefits(reco, locale)" />
        </q-menu>
      </q-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import { hasBenefits, getBenefits } from '@/utils/benefits'

const { locale, t } = useI18n()

defineProps<{
  /** Sustainability grade of the current habit; only shown when above zero. */
  bravo: number
  reco: string
  benefitsExpanded?: boolean
}>()
</script>

<style scoped lang="scss">
// Reads as a success note on either theme: a tinted surface rather than a
// near-white island on the dark page.
.bravo-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border: 1px solid var(--success-border);
  border-radius: $button-border-radius;
  background-color: var(--success-bg);
  color: var(--success-color);
  font-size: 1rem;
}

.bravo-box__icon {
  flex-shrink: 0;
}

.bravo-box__text {
  flex: 1;
}

.bravo-box__action {
  flex-shrink: 0;
  margin-left: 16px;
}

.bravo-box__btn {
  background-color: #168654 !important;
  color: #fff !important;
  box-shadow: none;
}
</style>
