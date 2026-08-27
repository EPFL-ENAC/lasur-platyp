<template>
  <q-page>
    <div class="text-h4 q-pa-md text-title">{{ t('dashboard') }}</div>
    <div class="q-pa-md">
      <q-expansion-item
        v-model="isIntroductionExpanded"
        switch-toggle-side
        class="q-mb-lg"
        header-class="text-h6"
      >
        <template #header>
          <q-item-section>
            {{ t('welcome') }}
          </q-item-section>
        </template>

        <q-card flat>
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
      </q-expansion-item>

      <div class="text-h6 q-mb-sm">{{ t('statistics') }}</div>
      <dashboard-panel />
    </div>

    <data-protection-notice-dialog />
  </q-page>
</template>

<script setup lang="ts">
import IntroductionEn from '@/assets/markdown/introduction-en.md'
import IntroductionFr from '@/assets/markdown/introduction-fr.md'
import DashboardPanel from '@/components/DashboardPanel.vue'
import DataProtectionNoticeDialog from '@/components/DataProtectionNoticeDialog.vue'
import { isIndexIntroductionFirstView, markIndexIntroductionSeen } from '@/utils/localStorage'

const { t, locale } = useI18n()

const introductionText = computed(() => (locale.value === 'fr' ? IntroductionFr : IntroductionEn))

// Introduction is expanded by default on first visit
const isIntroductionExpanded = ref(isIndexIntroductionFirstView())

onMounted(() => {
  if (isIndexIntroductionFirstView()) {
    markIndexIntroductionSeen()
  }
})
</script>
