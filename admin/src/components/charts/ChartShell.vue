<template>
  <div class="chart-shell">
    <div class="chart-shell__frame" :style="frameStyle">
      <div :style="containerStyle" class="chart-shell__visual">
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
    </div>

    <div v-if="hasData" class="q-mt-md">
      <slot name="table" />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { CSSProperties } from 'vue'
import { downloadDataUrl, mergeImageWithLogo } from '@/utils/images'

interface Props {
  height?: number | undefined
  hasData: boolean
  showInfo?: boolean | undefined
  showTable?: boolean | undefined
  loading?: boolean | undefined
  noDataTitle?: string
  noDataText: string
  exportable?: boolean | undefined
  exportFileName?: string | undefined
  logoUrl?: string | undefined
  logoPadding?: number | undefined
  logoWidthRatio?: number | undefined
  captureRawImage?: () => Promise<string | null>
  // Turn the chart a quarter counter-clockwise (landscape chart on a portrait
  // page): +height+ is then its length along the page, its width the page's.
  rotated?: boolean | undefined
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

defineExpose({
  handleExport,
})

const exporting = ref(false)

const frameStyle = computed<CSSProperties>(() =>
  props.rotated
    ? { height: `${props.height}px`, position: 'relative', containerType: 'inline-size' }
    : {},
)

const containerStyle = computed<CSSProperties>(() =>
  props.rotated
    ? {
        // Swapped sides, the frame width (cqw) becoming the chart height;
        // shifted by its own length so the turn lands back in the frame.
        width: `${props.height}px`,
        height: '100cqw',
        position: 'absolute',
        top: 0,
        left: 0,
        transformOrigin: 'top left',
        transform: 'rotate(-90deg) translateX(-100%)',
      }
    : {
        height: `${props.height}px`,
        width: '100%',
        position: 'relative',
      },
)

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
/* Plain block around the sized chart area: the details dialog frames it, and
   a block with no explicit width always fits its parent, padding included. */
.chart-shell__frame {
  min-width: 0;
  overflow: hidden;
}

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
