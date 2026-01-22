<template>
  <q-dialog v-model="showDialog" persistent @hide="onHide">
    <q-card class="dialog-md">
      <q-card-actions>
        <div class="text-h6 q-ml-sm">{{ t(editMode ? 'edit' : 'add') }}</div>
        <q-space />
        <q-btn flat icon="close" color="primary" v-close-popup />
      </q-card-actions>
      <q-separator />

      <q-card-section>
        <q-form ref="form">
          <q-input
            filled
            v-model="selected.name"
            :label="t('name') + ' *'"
            lazy-rules
            :rules="[(val) => !!val || t('field_required')]"
          />
          <q-select
            filled
            v-model="selected.administrators"
            :label="t('company.administrators')"
            :hint="t('company.administrators_hint')"
            use-input
            use-chips
            multiple
            hide-dropdown-icon
            input-debounce="0"
            new-value-mode="add-unique"
            class="q-mb-md"
          />
          <q-input
            filled
            v-model="selected.contact_name"
            :label="t('company.contact_name')"
            :hint="t('company.contact_name_hint')"
            class="q-mb-md"
          />
          <q-input
            filled
            v-model="selected.contact_email"
            :label="t('company.contact_email')"
            :hint="t('company.contact_email_hint')"
            lazy-rules
            :rules="[
              (val) => !val || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val) || t('valid_email_required'),
            ]"
            class="q-mb-md"
          />
          <q-input
            filled
            v-model="selected.info_url"
            :label="t('company.info_url')"
            :hint="t('company.info_url_hint')"
            lazy-rules
            :rules="[(val) => !val || /^(http|https):/.test(val) || t('valid_url_required')]"
            class="q-mb-md"
          />
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

const form = ref()
const showDialog = ref(props.modelValue)
const selected = ref<Company>({
  name: '',
} as Company)
const editMode = ref(false)

watch(
  () => props.modelValue,
  (value) => {
    if (value) {
      // deep copy
      selected.value = JSON.parse(JSON.stringify(props.item))
      if (selected.value.administrators === undefined) {
        selected.value.administrators = []
      }
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
