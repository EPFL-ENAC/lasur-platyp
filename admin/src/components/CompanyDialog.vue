<template>
  <q-dialog v-model="showDialog" persistent @hide="onHide">
    <q-card class="dialog-sm">
      <q-card-actions>
        <div class="text-h6 q-ml-sm">{{ t(editMode ? 'edit' : 'add') }}</div>
        <q-space />
        <q-btn flat icon="close" color="primary" v-close-popup />
      </q-card-actions>
      <q-separator />

      <q-card-section>
        <q-input filled v-model="selected.name" :label="t('name') + ' *'" />
      </q-card-section>

      <q-separator />

      <q-card-actions align="right" class="bg-grey-3">
        <q-btn flat :label="t('cancel')" color="secondary" v-close-popup />
        <q-btn :label="t('save')" color="primary" @click="onSave" :disable="!isValid" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import type { Company } from 'src/models'
import { notifyError } from 'src/utils/notify'

interface DialogProps {
  modelValue: boolean
  item: Company | undefined
}

const props = defineProps<DialogProps>()
const emit = defineEmits(['update:modelValue', 'saved'])

const { t } = useI18n()
const services = useServices()
const service = services.make('company')

const showDialog = ref(props.modelValue)
const selected = ref<Company>({
  name: '',
} as Company)
const editMode = ref(false)

const isValid = computed(() => {
  return selected.value.name?.trim().length > 0
})

watch(
  () => props.modelValue,
  (value) => {
    if (value) {
      // deep copy
      selected.value = JSON.parse(JSON.stringify(props.item))
      editMode.value = selected.value.id !== undefined
    }
    showDialog.value = value
  },
)

function onHide() {
  showDialog.value = false
  emit('update:modelValue', false)
}

async function onSave() {
  if (selected.value === undefined) return
  if (selected.value.id) {
    service
      .update(selected.value.id, selected.value)
      .then(() => {
        emit('saved', selected.value)
        onHide()
      })
      .catch((err) => {
        notifyError(err.message)
      })
  } else {
    service
      .create(selected.value)
      .then(() => {
        emit('saved', selected.value)
        onHide()
      })
      .catch((err) => {
        notifyError(err.message)
      })
  }
}
</script>
