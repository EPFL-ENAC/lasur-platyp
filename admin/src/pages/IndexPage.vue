<template>
  <q-page>
    <div class="text-h5 q-pa-md">{{ t('dashboard') }}</div>
    <q-separator />
    <div v-if="authStore.isAdmin" class="bg-info text-white q-pt-sm q-pb-sm q-pl-md q-pr-md">
      {{ t('your_role', { role: t('role.platyp-admin') }) }}
    </div>
    <div class="q-pa-md">
      <q-card>
        <q-banner class="bg-grey-2 q-mb-md">
          {{ t('introduction_text') }}
          <template v-slot:action>
            <q-btn flat icon="fa-solid fa-book" size="sm" :label="t('documentation')" to="/doc" />
          </template>
        </q-banner>
      </q-card>
      <div class="text-h6 q-mb-sm">{{ t('statistics') }}</div>
      <dashboard-panel />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import DashboardPanel from 'src/components/DashboardPanel.vue'

const { t } = useI18n()
const authStore = useAuthStore()
</script>
