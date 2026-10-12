<template>
  <q-dialog v-if="authStore.isAuthenticated" v-model="showDataProtectionNotice" @hide="onClose">
    <q-card>
      <q-card-section>
        <div class="text-h6">{{ t('data_protection_notice.title') }}</div>
      </q-card-section>

      <q-card-section class="q-py-none">
        <q-markdown :src="t('data_protection_notice.content')" no-heading-anchor-links />
      </q-card-section>

      <q-card-actions>
        <q-toggle v-model="preferences.doNotShowNotice" :label="t('do_not_show_again')" />
      </q-card-actions>

      <q-card-actions align="right">
        <q-btn flat :label="t('close')" color="primary" v-close-popup @click="onClose" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { isFirstVisit } from '@/utils/localStorage'

const preferences = usePreferencesStore()
const authStore = useAuthStore()
const { t } = useI18n()

const showDataProtectionNotice = ref(
  !preferences.doNotShowNotice &&
    !preferences.hasAlreadyShownDataProtectionNoticeThisTime &&
    // On the first visit the user is redirected to the doc page (privacy
    // policy included) right after this page mounts — don't pop the notice
    // over that flash; it shows the next time the dashboard is viewed.
    !isFirstVisit(),
)

function onClose() {
  preferences.hasAlreadyShownDataProtectionNoticeThisTime = true
}
</script>
