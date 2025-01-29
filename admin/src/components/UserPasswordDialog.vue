<template>
  <q-dialog v-model="showDialog" persistent @hide="onHide">
    <q-card class="dialog-sm">
      <q-card-actions>
        <div class="text-h6 q-ml-sm">{{ t('reset_password') }}</div>
        <q-space />
        <q-btn flat icon="close" color="primary" v-close-popup />
      </q-card-actions>
      <q-separator />

      <q-card-section>
        <q-input
          filled
          v-model="password"
          type="password"
          :label="t('password') + ' *'"
          :hint="t('password_hint')"
          class="q-mb-md"
        />
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
  item: AppUser
}

const props = defineProps<DialogProps>()
const emit = defineEmits(['update:modelValue', 'saved'])

const { t } = useI18n()
const usersStore = useUsersStore()

const showDialog = ref(props.modelValue)
const password = ref('')
const isValid = computed(() => {
  return password.value?.trim().length > 0
})

watch(
  () => props.modelValue,
  (value) => {
    showDialog.value = value
  },
)

function onHide() {
  showDialog.value = false
  emit('update:modelValue', false)
}

async function onSave() {
  if (password.value) {
    usersStore
      .update_password(props.item, password.value)
      .then(() => {
        emit('saved')
        onHide()
      })
      .catch(notifyError)
  }
}
</script>
