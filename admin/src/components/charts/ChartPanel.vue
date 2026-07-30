<template>
  <div>
    <div class="text-h6 text-primary q-mb-md">{{ title }}</div>
    <q-markdown
      v-if="description"
      class="compact q-mt-sm"
      :class="!details ? 'q-mb-md' : ''"
      :src="description"
    />
    <div v-if="details" class="q-mb-md">
      <q-markdown class="compact" :src="details" />
    </div>

    <q-card flat>
      <q-card-section>
        <slot></slot>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string
  description?: string
  details?: string
  inline?: boolean
}

defineProps<Props>()
</script>
