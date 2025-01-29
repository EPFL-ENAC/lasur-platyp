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
        <q-input
          filled
          v-model="selected.email"
          :disable="editMode"
          :label="t('email') + ' *'"
          class="q-mb-md"
        />
        <q-input
          v-if="!editMode"
          filled
          v-model="selected.password"
          type="password"
          :label="t('password') + ' *'"
          :hint="t('password_hint')"
          class="q-mb-md"
        />
        <q-input
          filled
          v-model="selected.first_name"
          :label="t('first_name') + ' *'"
          class="q-mb-md"
        />
        <q-input
          filled
          v-model="selected.last_name"
          :label="t('last_name') + ' *'"
          class="q-mb-md"
        />
        <q-checkbox v-model="selected.enabled" :label="t('enabled')" class="q-mb-md" />
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
import type { AppUser } from 'src/models'
import { notifyError } from 'src/utils/notify'

interface DialogProps {
  modelValue: boolean
  item: AppUser | undefined
}

const props = defineProps<DialogProps>()
const emit = defineEmits(['update:modelValue', 'saved'])

const { t } = useI18n()
const usersStore = useUsersStore()

const showDialog = ref(props.modelValue)
const selected = ref<AppUser>({
  email: '',
} as AppUser)
const editMode = ref(false)

const isValid = computed(() => {
  return selected.value.email?.trim().length > 0
})

watch(
  () => props.modelValue,
  (value) => {
    if (value) {
      // deep copy
      selected.value = JSON.parse(JSON.stringify(props.item))
      if (selected.value.enabled === undefined) {
        selected.value.enabled = true
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
  if (selected.value === undefined) return
  if (selected.value.id) {
    usersStore
      .update(selected.value)
      .then(() => {
        emit('saved', selected.value)
        onHide()
      })
      .catch(notifyError)
  } else {
    usersStore
      .create(selected.value)
      .then(() => {
        emit('saved', selected.value)
        onHide()
      })
      .catch(notifyError)
  }
}
</script>
