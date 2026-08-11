<template>
  <div :class="wrapperClass">
    <div class="q-pa-md">
      <q-item-label v-if="indexLabel" class="text-body1 text-primary text-bold">
        {{ indexLabel }}
      </q-item-label>

      <div v-if="bravo !== undefined && bravo > 0" class="bravo-box">
        {{ t(`bravo.${bravo}`) }}
      </div>

      <q-item-label v-if="bravo !== 2" :class="recoClass || 'text-h5'">
        {{ recoLabel }}
      </q-item-label>

      <BenefitsPanel :reco="reco" class="q-mt-sm" :expanded="!!benefitsExpanded" />

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
import BenefitsPanel from 'src/components/form/steps/BenefitsPanel.vue'

const { t } = useI18n()

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
  color: #168654;
  background-color: #f5fbf9;
  border: 1px solid #cedfd7;
  border-radius: 8px;
  padding: 8px 16px;
  margin-bottom: 16px;
  font-size: 16px;
}
</style>
