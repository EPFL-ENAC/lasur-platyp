<template>
  <q-page>
    <div class="text-h5 q-pa-md">{{ t('dashboard') }}</div>
    <q-separator />
    <div class="q-pa-md">
      {{
        t('your_role', { role: t(authStore.isAdmin ? 'role.platyp-admin' : 'role.platyp-user') })
      }}
    </div>
  </q-page>
</template>

<script setup lang="ts">
const { t } = useI18n()
const authStore = useAuthStore()
</script>
