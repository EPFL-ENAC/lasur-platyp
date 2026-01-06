<template>
  <q-page>
    <div class="text-h5 q-pa-md">{{ t('legal_notice') }}</div>
    <q-separator />
    <div class="q-pa-md">
      <q-markdown
        :src="locale === 'fr' ? TermsConditionsFr : TermsConditionsEn"
        no-heading-anchor-links
        class="q-mb-xl"
      />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import TermsConditionsEn from 'src/assets/docs/en/terms-conditions.md'
import TermsConditionsFr from 'src/assets/docs/fr/terms-conditions.md'

const { locale, t } = useI18n()
</script>
