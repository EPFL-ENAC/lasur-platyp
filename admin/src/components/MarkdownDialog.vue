<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide">
    <q-card class="dialog-lg">
      <q-card-section v-if="props.title">
        <div class="text-h6">{{ props.title }}</div>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <q-markdown :src="props.text" no-heading-anchor-links />
        <q-checkbox v-if="props.checkboxLabel" v-model="checked" :label="props.checkboxLabel" />
      </q-card-section>

      <q-separator />

      <q-card-actions align="right">
        <q-btn
          v-if="props.canCancel"
          :label="t('cancel')"
          color="primary"
          outline
          @click="onDialogCancel"
          v-close-popup
        />
        <q-btn :label="t('ok')" color="primary" @click="onDialogOK(checked)" v-close-popup />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { useDialogPluginComponent } from 'quasar'

const { t } = useI18n()

interface DialogProps {
  title?: string | undefined
  text: string
  canCancel?: boolean
  checkboxLabel?: string | undefined
}

const props = defineProps<DialogProps>()
defineEmits([...useDialogPluginComponent.emits])

const checked = ref(true)

const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent()
</script>
