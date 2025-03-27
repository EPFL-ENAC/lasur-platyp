<template>
  <div>
    <div v-if="hasBenefits(reco)">
      <div v-if="showBenefits.includes(reco)" class="bg-primary q-mt-md q-pa-sm rounded-borders">
        <q-markdown :src="getBenefits(reco, locale)" />
      </div>
      <q-btn
        v-if="showBenefits.includes(reco)"
        @click="showBenefits = showBenefits.filter((b) => b !== reco)"
        :label="t('benefits.hide')"
        color="grey-4"
        size="md"
        icon-right="keyboard_arrow_up"
        no-caps
        flat
        dense
      />
      <q-btn
        v-else
        @click="showBenefits = [...showBenefits, reco]"
        :label="t('benefits.show')"
        color="white"
        size="md"
        icon-right="keyboard_arrow_down"
        no-caps
        flat
        dense
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { hasBenefits, getBenefits } from 'src/utils/benefits'

const { locale, t } = useI18n()

defineProps<{
  reco: string
}>()

const showBenefits = ref<string[]>([])
</script>
