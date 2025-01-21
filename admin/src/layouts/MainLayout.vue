<template>
  <q-layout view="hHh lpR fFf">
    <q-header bordered class="bg-white text-grey-10">
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />

        <q-toolbar-title>
          <img src="modus.svg" height="25px" />
          {{ t('main.brand') }}
        </q-toolbar-title>

        <img src="EPFL.svg" height="20px" />
        <q-btn-dropdown flat no-caps :label="username">
          <q-list>
            <q-item clickable v-close-popup @click="onLogout" v-if="authStore.isAuthenticated">
              <q-item-section avatar>
                <q-icon name="logout" size="xs" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ t('logout') }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item clickable v-close-popup :to="'/'">
          <q-item-section avatar>
            <q-icon name="dashboard" />
          </q-item-section>
          <q-item-section>
            <q-item-label header>{{ t('dashboard') }}</q-item-label>
          </q-item-section>
        </q-item>

        <q-item-label class="text-h6" header>{{ t('content') }}</q-item-label>
        <q-item clickable v-close-popup :to="'/companies'">
          <q-item-section avatar>
            <q-icon name="fa-solid fa-building" size="xs" />
          </q-item-section>
          <q-item-section>
            <q-item-label header>{{ t('companies') }}</q-item-label>
          </q-item-section>
        </q-item>
        <q-item clickable v-close-popup :to="'/case-reports'">
          <q-item-section avatar>
            <q-icon name="fa-brands fa-wpforms" size="xs" />
          </q-item-section>
          <q-item-section>
            <q-item-label header>{{ t('case_reports') }}</q-item-label>
          </q-item-section>
        </q-item>

        <q-item-label class="text-h6" header>{{ t('help') }}</q-item-label>
        <q-item clickable v-close-popup :to="'/cookbook'">
          <q-item-section avatar>
            <q-icon name="fa-solid fa-bowl-rice" size="xs" />
          </q-item-section>
          <q-item-section>
            <q-item-label header>{{ t('cookbook') }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
const authStore = useAuthStore()
const { t } = useI18n()

onMounted(() => {
  authStore.init().then(() => {
    if (!authStore.isAuthenticated) {
      return authStore.login()
    }
  })
})

watch(
  () => authStore.isAuthenticated,
  () => {
    if (authStore.isAuthenticated) {
      console.log('Authenticated')
    } else {
      console.log('Not authenticated')
    }
  },
)

const leftDrawerOpen = ref(false)

const username = computed(() => authStore.profile?.email)

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

function onLogout() {
  authStore.logout()
}
</script>
