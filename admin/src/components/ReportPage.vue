<template>
  <div :class="{ page: true, 'title-page': props.isTitle }">
    <div aria-hidden="true" class="background-dots"></div>

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

<style scoped lang="scss">
.title-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

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
  padding: calc(var(--page-margins-y) * 0.5) var(--page-margins-x);
  width: 100%;
  text-align: right;
}

footer::after {
  counter-increment: page-counter;
  content: counter(page-counter);
}

// Dot grid, same as the app: 3px dots on a 30px pitch, dissolving towards the
// left and right edges via a mask -- no image asset needed. Painted above the
// white page background and below all content.
.background-dots {
  --dot-color: #{$brand-purple-200};
  --dot-fade: linear-gradient(90deg, transparent 0%, #000 45%, #000 55%, transparent 100%);

  position: absolute;
  inset: 0;
  z-index: -1;

  background-image: radial-gradient(circle, var(--dot-color) 1.5px, transparent 1.5px);
  background-size: 30px 30px;
  opacity: 0.25;

  mask-image: var(--dot-fade);
  -webkit-mask-image: var(--dot-fade);
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
