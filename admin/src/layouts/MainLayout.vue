<template>
  <q-layout view="hHh lpR fFf">
    <q-header v-if="authStore.isAuthenticated" bordered class="bg-white text-grey-10">
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />

        <q-toolbar-title>
          <a href="https://modus-ge.ch/" target="_blank">
            <img src="modus.svg" height="25px" />
          </a>
          <span class="text-primary text-bold on-right">{{ t('main.brand') }}</span>
        </q-toolbar-title>

        <q-btn-dropdown flat dense :label="locale" class="on-left">
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
        <a href="https://www.epfl.ch" target="_blank">
          <img src="EPFL.svg" height="20px" class="on-left" />
        </a>
      </q-toolbar>
    </q-header>

    <q-drawer v-if="authStore.isAuthenticated" v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <template v-if="authStore.isAuthenticated">
          <q-item @click="onLogout">
            <q-item-section avatar>
              <q-icon name="fa-solid fa-user" size="xs" />
            </q-item-section>
            <q-item-section>
              <q-item-label header>{{ username }}</q-item-label>
            </q-item-section>
          </q-item>

          <q-item clickable @click="onLogout">
            <q-item-section avatar>
              <q-icon name="fa-solid fa-right-from-bracket" size="xs" />
            </q-item-section>
            <q-item-section>
              <q-item-label header>{{ t('logout') }}</q-item-label>
            </q-item-section>
          </q-item>

          <q-separator />
        </template>

        <q-item clickable :to="'/'">
          <q-item-section avatar>
            <q-icon name="dashboard" />
          </q-item-section>
          <q-item-section>
            <q-item-label header>{{ t('dashboard') }}</q-item-label>
          </q-item-section>
        </q-item>
        <q-item-label class="text-h6" header>{{ t('content') }}</q-item-label>
        <q-item clickable :to="'/companies'">
          <q-item-section avatar>
            <q-icon name="fa-solid fa-building" size="xs" />
          </q-item-section>
          <q-item-section>
            <q-item-label header>{{ t('companies') }}</q-item-label>
          </q-item-section>
        </q-item>
        <q-item clickable :to="'/records'">
          <q-item-section avatar>
            <q-icon name="fa-brands fa-wpforms" size="xs" />
          </q-item-section>
          <q-item-section>
            <q-item-label header>{{ t('records') }}</q-item-label>
          </q-item-section>
        </q-item>

        <q-item-label v-if="authStore.isAdmin" class="text-h6" header>{{
          t('administration')
        }}</q-item-label>
        <q-item v-if="authStore.isAdmin" clickable :to="'/users'">
          <q-item-section avatar>
            <q-icon name="fa-solid fa-users" size="xs" />
          </q-item-section>
          <q-item-section>
            <q-item-label header>{{ t('users') }}</q-item-label>
          </q-item-section>
        </q-item>

        <q-item-label class="text-h6" header>{{ t('help') }}</q-item-label>
        <q-item clickable :to="'/cookbook'">
          <q-item-section avatar>
            <q-icon name="fa-solid fa-bowl-rice" size="xs" />
          </q-item-section>
          <q-item-section>
            <q-item-label header>{{ t('cookbook') }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container v-if="authStore.isAuthenticated">
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { Cookies } from 'quasar'
import { locales } from 'boot/i18n'

const authStore = useAuthStore()
const { locale, t } = useI18n()
const router = useRouter()

const loggedOut = ref(false)
const leftDrawerOpen = ref(false)

const username = computed(() => authStore.profile?.email)
const localeOptions = computed(() => {
  return locales.map((key) => ({
    label: key.toUpperCase(),
    value: key,
  }))
})

onMounted(() => {
  authStore.init().then(() => {
    if (!authStore.isAuthenticated) {
      router.push({ path: '/signin' })
    } else {
      loggedOut.value = false
    }
  })
})

watch(
  () => authStore.isAuthenticated,
  () => {
    if (!authStore.isAuthenticated) {
      router.push('/signin')
    }
  },
)

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

function onLogout() {
  loggedOut.value = true
  authStore.logout()
}

function onLocaleSelection(localeOpt: { label: string; value: string }) {
  locale.value = localeOpt.value
  Cookies.set('locale', localeOpt.value)
}
</script>
