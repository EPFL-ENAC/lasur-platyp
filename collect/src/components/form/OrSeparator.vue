<template>
  <div class="or-separator">
    <span class="or-separator__label">{{ t('or') }}</span>
  </div>
</template>

<script setup lang="ts">
// A hairline rule either side of an "or", for two alternative ways of
// answering the same question.
const { t } = useI18n()
</script>

<style scoped lang="scss">
.or-separator {
  display: flex;
  align-items: center;
  gap: 16px;
  color: var(--hint-color);

  &::before,
  &::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--secondary-border-color);
  }
}

.or-separator__label {
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
</style>
