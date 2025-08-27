<template>
  <div>
    <div class="text-h5 text-center q-mb-xl q-mb-md">
      {{ t('form.final') }}
    </div>
    <InfoPanel />
  </div>
</template>

<script setup lang="ts">
import InfoPanel from 'src/components/form/InfoPanel.vue'
const { t } = useI18n()
</script>
