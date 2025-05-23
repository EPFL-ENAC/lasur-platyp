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
        <q-form ref="form">
          <participant-form v-model="selected" />
        </q-form>
      </q-card-section>

      <q-separator />

      <q-card-actions align="right" class="bg-grey-3">
        <q-btn flat :label="t('cancel')" color="secondary" v-close-popup />
        <q-btn :label="t('save')" color="primary" @click="onSave" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import type { Participant } from 'src/models'
import { notifyError } from 'src/utils/notify'
import ParticipantForm from 'src/components/ParticipantForm.vue'

interface DialogProps {
  modelValue: boolean
  item: Participant | undefined
}

const props = defineProps<DialogProps>()
const emit = defineEmits(['update:modelValue', 'saved'])

const { t } = useI18n()
const services = useServices()
const service = services.make('participant')

const form = ref()
const showDialog = ref(props.modelValue)
const selected = ref<Participant>({
  identifier: '',
} as Participant)
const editMode = ref(false)

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
  const valid = await form.value.validate()
  if (!valid) return
  if (selected.value === undefined) return
  if (selected.value.id) {
    service
      .update(selected.value.id, selected.value)
      .then(() => {
        emit('saved', selected.value)
        onHide()
      })
      .catch(notifyError)
  } else {
    service
      .create(selected.value)
      .then(() => {
        emit('saved', selected.value)
        onHide()
      })
      .catch(notifyError)
  }
}
</script>
