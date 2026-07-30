<template>
  <div>
    <div class="text-h6 text-primary q-mb-md">{{ title }}</div>
    <q-markdown v-if="description" class="compact q-mt-sm q-mb-md" :src="description" />
    <div v-if="!noDetails" class="q-mb-md">
      <a
        href="#"
        v-if="!inline"
        flat
        no-caps
        color="primary"
        class="q-mb-md text-secondary row items-center inline-flex no-wrap"
        @click.prevent="showDialog = true"
        >{{ t('more_details') }}</a
      >
    </div>
    <q-card flat>
      <q-card-section>
        <slot></slot>
      </q-card-section>
    </q-card>

    <q-dialog
      v-model="showDialog"
      :maximized="true"
      transition-show="slide-up"
      transition-hide="slide-down"
    >
      <q-card flat>
        <q-card-section>
          <div class="chart-panel-dialog-content">
            <div class="text-h6 text-primary q-mb-md">{{ title }}</div>
            <q-markdown v-if="description" class="compact q-mt-sm q-mb-md" :src="description" />
            <slot></slot>
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn no-caps :label="t('close')" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup lang="ts">
import { chartPanelDialogOpenKey } from './commons'

const { t } = useI18n()

interface Props {
  title: string
  description?: string
  inline?: boolean
  noDetails?: boolean
}

defineProps<Props>()

const showDialog = ref(false)

provide(chartPanelDialogOpenKey, showDialog)
</script>

<style scoped>
.chart-panel-dialog-content {
  width: 100%;
  max-width: 1024px;
  margin: 0 auto;
}
</style>
