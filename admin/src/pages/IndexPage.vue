<template>
  <q-page>
    <div class="text-h5 q-pa-md">{{ t('dashboard') }}</div>
    <q-separator />
    <div class="q-pa-md">
      <pre>{{ authStore.isAdmin ? 'admin' : 'not admin' }}</pre>
    </div>
  </q-page>
</template>

<script setup lang="ts">
const { t } = useI18n()
const authStore = useAuthStore()
</script>
