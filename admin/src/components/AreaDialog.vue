<template>
  <q-dialog v-model="showDialog" persistent @hide="onHide">
    <q-card class="dialog-xl">
      <q-card-section>
        <div class="text-h6">{{ props.title }}</div>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <div v-if="props.text" class="q-mb-md">
          {{ props.text }}
        </div>
        <area-input v-model="area" :zoom="12" />
      </q-card-section>

      <q-separator />

      <q-card-actions align="right" class="bg-grey-3">
        <q-btn flat :label="t('cancel')" color="secondary" @click="onCancel" v-close-popup />
        <q-btn flat :label="t('select')" color="primary" @click="onSelect" v-close-popup />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import AreaInput from 'src/components/AreaInput.vue'
const { t } = useI18n()

interface DialogProps {
  modelValue: boolean
  title: string
  text?: string
}

const props = defineProps<DialogProps>()
const emit = defineEmits(['update:modelValue', 'select', 'cancel'])

const area = ref<GeoJSON.FeatureCollection | undefined>()

const showDialog = ref(props.modelValue)

watch(
  () => props.modelValue,
  (value) => {
    showDialog.value = value
    area.value = undefined
  },
)

function onHide() {
  emit('update:modelValue', false)
}

function onCancel() {
  emit('cancel')
}

function onSelect() {
  emit('select', area.value)
}
</script>
