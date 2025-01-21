<template>
  <q-layout view="hHh lpR fFf">
    <q-header bordered class="bg-white text-grey-10">
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />

        <q-toolbar-title>
          <a href="https://modus-ge.ch/" target="_blank">
            <img src="modus.svg" height="25px" />
          </a>
          <span class="text-primary text-bold on-right">{{ t('main.brand') }}</span>
        </q-toolbar-title>

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
        <q-item clickable :to="'/case-reports'">
          <q-item-section avatar>
            <q-icon name="fa-brands fa-wpforms" size="xs" />
          </q-item-section>
          <q-item-section>
            <q-item-label header>{{ t('case_reports') }}</q-item-label>
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

    <login-dialog v-model="showLogin" />

    <q-page-container v-if="authStore.isAuthenticated">
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import LoginDialog from 'src/components/LoginDialog.vue'

const authStore = useAuthStore()
const { t } = useI18n()

const showLogin = ref(false)
const loggedOut = ref(false)

onMounted(() => {
  authStore.init().then(() => {
    if (!authStore.isAuthenticated) {
      showLogin.value = true
    } else {
      loggedOut.value = false
    }
  })
})

watch(
  () => authStore.isAuthenticated,
  () => {
    if (!authStore.isAuthenticated && !loggedOut.value) {
      showLogin.value = true
    }
  },
)

const leftDrawerOpen = ref(false)

const username = computed(() => authStore.profile?.email)

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

function onLogout() {
  loggedOut.value = true
  authStore.logout()
}
</script>
