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
      <div class="text-h5 q-mb-md">{{ t('statistics') }}</div>
      <div v-if="stats.loading">
        <q-spinner-dots size="md" color="primary" />
      </div>
      <div v-else>
        <div class="text-h6 q-mb-md">{{ t('stats.equipments') }}</div>
        <div>{{ stats.frequencies.equipments }}</div>
        <div class="text-h6 q-mt-md q-mb-md">{{ t('stats.constraints') }}</div>
        <div>{{ stats.frequencies.constraints }}</div>
        <div class="text-h6 q-mt-md q-mb-md">{{ t('stats.travel_time') }}</div>
        <div>{{ stats.frequencies.travel_time }}</div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
const { t } = useI18n()
const authStore = useAuthStore()
const stats = useStats()

onMounted(() => {
  stats.loadStats()
})
</script>
