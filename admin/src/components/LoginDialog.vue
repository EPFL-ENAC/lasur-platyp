<template>
  <q-dialog v-model="showDialog" persistent @hide="onHide" backdrop-filter="blur(8px)">
    <q-card>
      <q-card-actions class="flex justify-center q-mt-xl q-ml-xl q-mr-xl q-mb-xs">
        <img src="modus.svg" height="50px" />
      </q-card-actions>
      <q-card-actions class="flex justify-center">
        <span class="text-primary text-h5 on-right">{{ t('main.brand') }}</span>
      </q-card-actions>
      <q-card-actions class="flex justify-center q-mt-md q-ml-xl q-mr-xl q-mb-xl">
        <q-btn outline :label="t('login')" color="primary" @click="onLogin" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
interface DialogProps {
  modelValue: boolean
}

const props = defineProps<DialogProps>()
const emit = defineEmits(['update:modelValue', 'saved'])

const { t } = useI18n()
const authStore = useAuthStore()
const showDialog = ref(props.modelValue)

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

async function onLogin() {
  authStore.login()
}
</script>
