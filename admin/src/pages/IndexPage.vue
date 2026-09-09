<template>
  <q-page class="q-pa-lg">
    <div class="title-bar page-title-bar">
      <div class="text-subtitle2">{{ t('dashboard') }}</div>
      <q-btn
        flat
        no-caps
        icon="fa-regular fa-file-lines"
        icon-right="arrow_outward"
        :label="t('documentation')"
        to="/doc"
        class="doc-btn"
      />
    </div>
    <div>
      <div class="q-mb-xl">
        <h1 class="text-h4 q-mt-xs q-mb-md">{{ t('welcome') }}</h1>
        <p class="text-subtitle1 q-mb-md">{{ t('welcome_subtitle') }}</p>
        <details-panel>
          <q-markdown :src="introductionText" no-heading-anchor-links />
        </details-panel>
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

<style scoped lang="scss">
.page-title-bar {
  align-items: center;
  gap: 16px;
}

.page-title-bar .text-subtitle2 {
  flex: 1;
  min-width: 0;
}

// Same skin as the header controls
.q-btn.doc-btn {
  flex: none;
  height: 36px;
  min-height: 36px;
  padding: 0 12px;
  border: 1px solid $brand-purple-100;
  border-radius: 8px; // radius-default
  background-color: white;
  color: $brand-purple-800;
  font-size: 13px;
  font-weight: 600;
  box-shadow:
    0 1px 2px 0 rgba(10, 13, 18, 0.05),
    inset 0 -2px 0 0 rgba(10, 13, 18, 0.05);
}

.q-btn.doc-btn :deep(.q-icon) {
  font-size: 16px;
  color: $brand-purple-400;
}

.q-btn.doc-btn :deep(.q-btn__content) {
  gap: 6px;
}

.body--dark .q-btn.doc-btn {
  background-color: $brand-purple-800;
  border-color: $brand-purple-200;
  color: $brand-purple-50;
}
</style>
