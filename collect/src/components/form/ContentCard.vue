<template>
  <q-card flat class="content-card">
    <q-card-section>
      <slot />
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
// Surface for one block of survey content. It owns the gap to the next block so
// panels only have to list what they contain, not space it.
</script>

<style scoped lang="scss">
.content-card {
  margin-bottom: 24px;

  &:last-child {
    margin-bottom: 0;
  }
}
</style>
