<template>
  <q-page class="q-pa-lg">
    <div class="text-h6 text-title">{{ t('dashboard') }}</div>
    <div>
      <div class="q-mb-xl">
        <div class="text-h5">{{ t('welcome') }}</div>
        <div class="q-my-md">{{ t('welcome_subtitle') }}</div>
        <details-panel>
          <q-markdown :src="introductionText" no-heading-anchor-links />
        </details-panel>

        <div align="right">
          <q-btn
            flat
            icon="fa-solid fa-book"
            color="foreground"
            size="sm"
            :label="t('documentation')"
            to="/doc"
          />
        </div>
      </div>

      <dashboard-panel />
    </div>

    <data-protection-notice-dialog />
  </q-page>
</template>

<script setup lang="ts">
import DetailsPanel from '@/components/DetailsPanel.vue'
import IntroductionEn from '@/assets/markdown/introduction-en.md'
import IntroductionFr from '@/assets/markdown/introduction-fr.md'
import DashboardPanel from '@/components/DashboardPanel.vue'
import DataProtectionNoticeDialog from '@/components/DataProtectionNoticeDialog.vue'

const { t, locale } = useI18n()

const introductionText = computed(() => (locale.value === 'fr' ? IntroductionFr : IntroductionEn))
</script>
