<template>
  <div class="chart-shell">
    <div :style="containerStyle" class="chart-shell__visual">
      <div class="toolbar-overlay">
        <q-btn
          v-if="hasData && exportable"
          dense
          unelevated
          icon="download"
          :disable="loading || exporting || !captureRawImage"
          @click="handleExport"
        />
      </div>

      <div v-if="hasData" class="chart-shell__content">
        <slot />
      </div>

      <div v-else class="chart-shell__empty column items-center justify-center q-px-md">
        <div v-if="noDataTitle" class="text-h6 text-center">{{ noDataTitle }}</div>
        <div class="text-subtitle1 text-foreground text-center">
          {{ noDataText }}
        </div>
      </div>
    </div>

    <div v-if="showInfo && $slots.info" class="q-mt-md chart-text">
      <slot name="info" />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { CSSProperties } from 'vue'
import { downloadDataUrl, mergeImageWithLogo } from 'src/utils/images'

interface Props {
  height?: number | undefined
  hasData: boolean
  showInfo?: boolean | undefined
  loading?: boolean | undefined
  noDataTitle?: string
  noDataText: string
  exportable?: boolean | undefined
  exportFileName?: string | undefined
  logoUrl?: string | undefined
  logoPadding?: number | undefined
  logoWidthRatio?: number | undefined
  captureRawImage?: () => Promise<string | null>
}

const props = withDefaults(defineProps<Props>(), {
  height: 400,
  showInfo: false,
  loading: false,
  exportable: true,
  exportFileName: 'chart.png',
  logoUrl: '/admin/LOGO-VIOLET.svg',
  logoPadding: 24,
  logoWidthRatio: 0.12,
})

const exporting = ref(false)

const containerStyle = computed<CSSProperties>(() => ({
  height: `${props.height}px`,
  width: '100%',
  position: 'relative',
}))

async function handleExport() {
  if (exporting.value || props.loading || !props.hasData || !props.captureRawImage) {
    return
  }

  try {
    exporting.value = true

    const rawImage = await props.captureRawImage()
    if (!rawImage) {
      return
    }

    const finalImage = await mergeImageWithLogo(rawImage, props.logoUrl, {
      padding: props.logoPadding,
      logoWidthRatio: props.logoWidthRatio,
    })

    downloadDataUrl(finalImage, props.exportFileName)
  } finally {
    exporting.value = false
  }
}
</script>

<style scoped>
.chart-shell__visual {
  position: relative;
  width: 100%;
}

.chart-shell__content,
.chart-shell__empty {
  width: 100%;
  height: 100%;
}

.toolbar-overlay {
  position: absolute;
  top: 0;
  right: 1rem;
  z-index: 1000;
  display: flex;
  gap: 0.5rem;
}
</style>
