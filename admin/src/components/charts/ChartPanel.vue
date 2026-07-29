<template>
  <div>
    <div class="text-h6 text-primary q-mb-md">{{ title }}</div>
    <q-markdown v-if="description" class="compact q-mt-sm" :src="description" />
    <details-panel v-if="details" class="q-mb-md">
      <q-markdown class="compact" :src="details" />
    </details-panel>

    <q-card flat>
      <q-card-section>
        <slot></slot>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import DetailsPanel from 'src/components/DetailsPanel.vue'

defineProps({
  title: {
    type: String,
    default: '',
  },
  description: {
    type: String,
    default: '',
  },
  details: {
    type: String,
    default: '',
  },
})
</script>
