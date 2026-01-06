<template>
  <div v-if="hasBenefits(reco)">
    <q-btn
      :label="t('benefits.show')"
      color="white"
      size="md"
      icon-right="workspace_premium"
      no-caps
      flat
      dense
    >
      <q-menu class="q-mr-md" :max-width="'400px'">
        <div class="bg-white text-secondary q-pt-md q-pr-md q-pl-md rounded-borders">
          <q-markdown :src="getBenefits(reco, locale)" />
        </div>
      </q-menu>
    </q-btn>
  </div>
</template>

<script setup lang="ts">
import { hasBenefits, getBenefits } from 'src/utils/benefits'

const { locale, t } = useI18n()

defineProps<{
  reco: string
}>()
</script>
