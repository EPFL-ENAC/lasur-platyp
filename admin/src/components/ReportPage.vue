<template>
  <div :class="{ page: true, 'title-page': props.isTitle }">
    <header v-if="!props.isTitle">
      <img src="/admin/LOGO-VIOLET.svg" alt="logo" />

      <div>{{ t('mobility_statistics') }} - {{ props.orgNames?.join(', ') || '' }}</div>
    </header>

    <slot />

    <footer v-if="!props.isTitle"></footer>
  </div>
</template>

<script setup lang="ts">
interface Props {
  isTitle?: boolean
  orgNames?: string[]
}

const props = defineProps<Props>()

const { t } = useI18n()
</script>

<style scoped>
.title-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.page {
  width: 210mm;
  min-height: 297mm;
  padding: 10mm;
  margin-bottom: 30px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  position: relative;
  isolation: isolate;
  background-color: white;
}

.page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('/admin/PATTERN-JAUNE.svg');
  background-repeat: no-repeat;
  background-position: 0rem -5rem;
  background-size: cover;
  opacity: 0.1;
  z-index: -1;
}

header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 10mm;
}

header img {
  height: 10mm;
}

footer {
  position: absolute;
  bottom: 0;
  left: 0;
  padding: 5mm 10mm;
  width: 100%;
  text-align: right;
}

footer::after {
  counter-increment: page-counter;
  content: counter(page-counter);
}

@media print {
  @page {
    size: A4 portrait;
    margin: 0;
  }

  .page {
    width: 210mm !important;
    min-height: 297mm !important;
    margin: 0 !important;
    padding: 10mm !important;
    box-shadow: none !important;
    overflow: visible !important;

    page-break-after: always;
    break-after: page;
    page-break-inside: avoid;
    break-inside: avoid-page;

    print-color-adjust: exact;
    -webkit-print-color-adjust: exact;
  }

  .page:last-child {
    page-break-after: auto;
    break-after: auto;
  }

  .page > * {
    page-break-inside: avoid;
    break-inside: avoid-page;
  }
}
</style>
