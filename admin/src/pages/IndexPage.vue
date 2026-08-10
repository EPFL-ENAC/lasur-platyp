<template>
  <q-page>
    <div class="text-h3 q-pa-md text-title">{{ t('dashboard') }}</div>
    <div class="q-pa-md">
      <q-card flat class="q-mb-lg">
        <q-card-section class="q-pb-none">
          <q-markdown :src="introductionText" no-heading-anchor-links />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            icon="fa-solid fa-book"
            color="foreground"
            size="sm"
            :label="t('documentation')"
            to="/doc"
          />
        </q-card-actions>
      </q-card>

      <div class="text-h6 q-mb-sm">{{ t('statistics') }}</div>
      <dashboard-panel />
    </div>

    <data-protection-notice-dialog />
  </q-page>
</template>

<script setup lang="ts">
import IntroductionEn from 'src/assets/markdown/introduction-en.md'
import IntroductionFr from 'src/assets/markdown/introduction-fr.md'
import DashboardPanel from 'src/components/DashboardPanel.vue'
import DataProtectionNoticeDialog from 'src/components/DataProtectionNoticeDialog.vue'

const { t, locale } = useI18n()

const introductionText = computed(() => locale.value === 'fr' ? IntroductionFr : IntroductionEn)
</script>
