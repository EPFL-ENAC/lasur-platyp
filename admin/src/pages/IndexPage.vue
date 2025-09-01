<template>
  <q-page>
    <div class="text-h5 q-pa-md">{{ t('dashboard') }}</div>
    <q-separator />
    <div class="bg-info text-white q-pt-sm q-pb-sm q-pl-md q-pr-md">
      {{
        t('your_role', { role: t(authStore.isAdmin ? 'role.platyp-admin' : 'role.platyp-user') })
      }}
    </div>
    <div class="q-pa-md">
      <dashboard-panel />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import DashboardPanel from 'src/components/DashboardPanel.vue'
const { t } = useI18n()
const authStore = useAuthStore()
</script>
