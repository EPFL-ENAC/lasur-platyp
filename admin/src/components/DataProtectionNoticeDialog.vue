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
const preferences = usePreferencesStore()
const authStore = useAuthStore()
const { t } = useI18n()

const showDataProtectionNotice = ref(
  !preferences.doNotShowNotice && !preferences.hasAlreadyShownDataProtectionNoticeThisTime,
)

function onClose() {
  preferences.hasAlreadyShownDataProtectionNoticeThisTime = true
}
</script>
