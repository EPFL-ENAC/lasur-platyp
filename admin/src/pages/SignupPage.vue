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
                type="email"
                :label="t('email') + ' *'"
                lazy-rules
                :rules="[
                  (val) => !!val || t('field_required'),
                  (val) => /\S+@\S+\.\S+/.test(val) || t('error.invalid_email'),
                ]"
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
                class="q-mb-xl"
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
            <q-btn-dropdown flat dense :label="locale">
              <q-list>
                <q-item
                  clickable
                  v-close-popup
                  @click="onLocaleSelection(localeOpt)"
                  v-for="localeOpt in localeOptions"
                  :key="localeOpt.value"
                >
                  <q-item-section>
                    <q-item-label>{{ localeOpt.label }}</q-item-label>
                  </q-item-section>
                  <q-item-section avatar v-if="locale === localeOpt.value">
                    <q-icon color="primary" name="check" />
                  </q-item-section>
                </q-item>
              </q-list>
            </q-btn-dropdown>
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
              @click="onSignup"
            />
          </q-card-actions>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar'
import { Cookies, copyToClipboard } from 'quasar'
import type { AppUser } from 'src/models'
import { notifyError, notifySuccess } from 'src/utils/notify'
import { generatePassword } from 'src/utils/generate'
import { locales } from 'boot/i18n'

const $q = useQuasar()
const { t, locale } = useI18n()
const authStore = useAuthStore()
const usersStore = useUsersStore()
const router = useRouter()

const form = ref()
const showPassword = ref(false)
const selected = ref<AppUser>({
  email: '',
} as AppUser)

const localeOptions = computed(() => {
  return locales.map((key) => ({
    label: key.toUpperCase(),
    value: key,
  }))
})

function onLocaleSelection(localeOpt: { label: string; value: string }) {
  locale.value = localeOpt.value
  Cookies.set('locale', localeOpt.value)
}

onMounted(async () => {
  await authStore.init()
  if (authStore.isAuthenticated) {
    router.push('/')
  }
})

async function onSignup() {
  if (!(await form.value.validate())) {
    notifyError(t('error.form_invalid'))
    return
  }
  try {
    await usersStore.register(selected.value)
  } catch (error) {
    notifyError(error)
    return
  }
  router.push('/signin')
}

function onGeneratePassword() {
  selected.value.password = generatePassword()
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
