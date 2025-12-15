<template>
  <q-layout>
    <q-page-container>
      <q-page class="flex flex-center bg-blue-grey-1">
        <q-card :style="$q.screen.lt.sm ? { width: '80%' } : { width: '400px' }">
          <q-card-actions class="flex justify-center q-mt-lg q-ml-xl q-mr-xl q-mb-xs">
            <img src="modus.svg" height="50px" />
          </q-card-actions>
          <q-card-actions class="flex justify-center">
            <span class="text-primary text-h5 on-right">{{ t('main.brand') }}</span>
          </q-card-actions>
          <q-card-section class="q-mx-lg q-my-md q-pa-none">
            <q-form ref="form">
              <q-input
                filled
                v-model="selected.email"
                :label="t('email') + ' *'"
                lazy-rules
                :rules="[(val) => !!val || t('field_required')]"
                class="q-mb-sm"
              />
              <q-input
                filled
                v-model="selected.password"
                :type="showPassword ? 'text' : 'password'"
                :label="t('password') + ' *'"
                :hint="t('password_hint')"
                autocomplete="new-password"
                lazy-rules
                :rules="[(val) => !!val || t('field_required')]"
                class="q-mb-sm"
              >
                <template v-slot:append>
                  <q-icon
                    name="visibility"
                    size="xs"
                    class="cursor-pointer on-left"
                    @click="showPassword = !showPassword"
                  />
                  <q-icon
                    name="content_copy"
                    size="xs"
                    class="cursor-pointer on-left"
                    @click="onCopyPassword"
                  />
                  <q-icon name="electric_bolt" class="cursor-pointer" @click="onGeneratePassword" />
                </template>
              </q-input>
              <q-input
                filled
                v-model="selected.first_name"
                :label="t('first_name') + ' *'"
                lazy-rules
                :rules="[(val) => !!val || t('field_required')]"
                class="q-mb-sm"
              />
              <q-input
                filled
                v-model="selected.last_name"
                :label="t('last_name') + ' *'"
                lazy-rules
                :rules="[(val) => !!val || t('field_required')]"
                class="q-mb-sm"
              />
            </q-form>
          </q-card-section>
          <q-card-actions class="flex justify-center q-mx-lg q-mb-lg q-pa-none">
            <q-btn
              flat
              :label="t('signin')"
              :disable="!authStore.initialized"
              color="primary"
              to="/signin"
            />
            <q-space />
            <q-btn
              outline
              :label="t('signup')"
              :disable="!authStore.initialized"
              :loading="!authStore.initialized"
              color="primary"
              @click="onLogin"
            />
          </q-card-actions>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar'
import { copyToClipboard } from 'quasar'
import type { AppUser } from 'src/models'
import { notifyError, notifySuccess } from 'src/utils/notify'
import { generateToken } from 'src/utils/generate'

const $q = useQuasar()
const { t } = useI18n()
const authStore = useAuthStore()
const router = useRouter()

const form = ref()
const showPassword = ref(false)
const selected = ref<AppUser>({
  email: '',
} as AppUser)

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

function onGeneratePassword() {
  selected.value.password = generateToken(12)
}

function onCopyPassword() {
  if (selected.value.password === undefined) return
  copyToClipboard(selected.value.password)
    .then(() => {
      notifySuccess('password_copied')
    })
    .catch(notifyError)
}
</script>
