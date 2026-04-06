<template>
  <q-page>
    <div class="text-h3 q-pa-md text-primary-dark">{{ t('dashboard') }}</div>
    <div class="q-pa-md">
      <q-card flat class="q-mb-lg">
        <q-card-section>
          {{ t('introduction_text') }}
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            icon="fa-solid fa-book"
            color="secondary"
            size="sm"
            :label="t('documentation')"
            to="/doc"
          />
        </q-card-actions>
      </q-card>

      <div class="text-h6 q-mb-sm">{{ t('statistics') }}</div>
      <dashboard-panel />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import DashboardPanel from 'src/components/DashboardPanel.vue'

const { t } = useI18n()
</script>
