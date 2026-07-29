<template>
  <div>
    <div class="text-h6 text-primary q-mb-md">{{ title }}</div>
    <q-markdown
      v-if="description"
      class="compact q-mt-sm"
      :class="!details ? 'q-mb-md' : ''"
      :src="description"
    />
    <details-panel v-if="details" :inline="inline" class="q-mb-md">
      <q-markdown class="compact" :src="details" />
      <slot name="details"></slot>
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

interface Props {
  title: string
  description?: string
  details?: string
  inline?: boolean
}

defineProps<Props>()
</script>
