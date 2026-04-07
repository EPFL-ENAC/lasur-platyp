<template>
  <q-page>
    <h4 class="text-h4 q-pa-md q-ma-none text-title">{{ t('legal_notice') }}</h4>
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
