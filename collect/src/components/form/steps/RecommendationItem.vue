<template>
  <div :class="wrapperClass">
    <div class="q-pa-md">
      <q-item-label
        v-if="indexLabel"
        class="text-body1 text-primary text-bold"
      >
        {{ indexLabel }}
      </q-item-label>

      <q-item-label :class="recoClass || 'text-h5'">
        {{ recoLabel }}
      </q-item-label>

      <BenefitsPanel :reco="reco" class="q-mt-sm" :expanded="!!benefitsExpanded" />

      <slot />

      <q-item-label
        v-if="actions?.length"
        class="text-body1 text-green-2 text-bold q-mt-md"
      >
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