<template>
  <q-layout>
    <q-page-container>
      <q-page class="flex flex-center bg-blue-grey-1">
        <q-card :style="$q.screen.lt.sm ? { width: '80%' } : { width: '360px' }">
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
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar'
import { notifyError } from 'src/utils/notify'

const $q = useQuasar()
const { t } = useI18n()
const authStore = useAuthStore()
const router = useRouter()

onMounted(async () => {
  await authStore.init()
  if (authStore.isAuthenticated) {
    router.push('/')
  }
})

async function onLogin() {
  try {
    await authStore.login()
  } catch (error) {
    notifyError(error)
    return
  }
  router.push('/')
}
</script>
