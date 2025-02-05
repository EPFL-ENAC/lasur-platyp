<template>
  <q-page class="row items-center justify-evenly bg-secondary text-white">
    <div>
      <div v-if="collector.loading">
        <q-spinner-grid color="white" size="50px" />
      </div>
      <div v-else>
        {{ t('welcome', { brand: t('main.brand') }) }}
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
const { t } = useI18n()
const collector = useCollector()
</script>
