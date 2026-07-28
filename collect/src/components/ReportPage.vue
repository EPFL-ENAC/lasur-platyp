<template>
  <div class="page">
    <slot />
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>

.page {
  --page-margins-x: 20mm;
  --page-margins-y: 15mm;

  width: 210mm;
  min-height: 297mm;
  padding: var(--page-margins-y) var(--page-margins-x);
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
  background-image: url('/PATTERN-VIOLET.svg');
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
  padding: calc(var(--page-margins-y) * 0.5) var(--page-margins-x);
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
    padding: var(--page-margins-y) var(--page-margins-x) !important;
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
