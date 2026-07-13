<template>
  <div v-if="hasBenefits(reco)">
    <div v-if="expanded" class="bg-white text-secondary rounded-borders q-pa-sm">
      <q-markdown :src="getBenefits(reco, locale)" />
    </div>

    <q-btn
      v-else
      :label="t('benefits.show')"
      color="foreground"
      size="md"
      icon-right="workspace_premium"
      no-caps
      dense
    >
      <q-menu class="q-mr-md bg-white text-secondary rounded-borders q-pa-md" :max-width="'400px'">
        <q-markdown :src="getBenefits(reco, locale)" />
      </q-menu>
    </q-btn>
  </div>
</template>

<script setup lang="ts">
import { hasBenefits, getBenefits } from 'src/utils/benefits'

const { locale, t } = useI18n()

withDefaults(
  defineProps<{
    reco: string
    expanded?: boolean
  }>(),
  {
    expanded: false,
  },
)
</script>
