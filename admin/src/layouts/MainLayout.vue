<template>
  <q-layout view="hHh LpR lff">
    <q-header v-if="authStore.isAuthenticated" bordered class="bg-nav">
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          color="foreground"
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title class="logos">
          <a href="https://modus-ge.ch/" target="_blank" class="logo" rel="noopener noreferrer">
            <img
              :src="$q.dark.isActive ? '/admin/LOGO-JAUNE.svg' : '/admin/LOGO-VIOLET.svg'"
              height="32px"
            />
          </a>
        </q-toolbar-title>

        <q-btn-dropdown flat dense color="foreground" :label="locale" class="on-left">
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
          <img src="/admin/EPFL.svg" height="20px" class="on-left" />
        </a>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-if="authStore.isAuthenticated"
      v-model="leftDrawerOpen"
      show-if-above
      bordered
      class="bg-nav text-foreground"
    >
      <div class="nav-wrapper">
        <q-list class="nav-list">
          <q-item class="text-foreground" clickable :to="'/'" exact dense>
            <q-item-section avatar>
              <q-icon name="dashboard" />
            </q-item-section>
            <q-item-section>
              <q-item-label header class="text-foreground text-weight-medium q-pl-sm q-py-sm">{{
                t('dashboard')
              }}</q-item-label>
            </q-item-section>
          </q-item>
          <q-item-label
            class="text-caption text-weight-bold text-foreground q-mt-xs q-pb-xs"
            header
            >{{ t('content') }}</q-item-label
          >
          <q-item class="text-foreground" clickable :to="'/companies'" dense>
            <q-item-section avatar>
              <q-icon name="fa-solid fa-building" size="xs" />
            </q-item-section>
            <q-item-section>
              <q-item-label header class="text-foreground text-weight-medium q-pl-sm q-py-sm">{{
                t('companies')
              }}</q-item-label>
            </q-item-section>
          </q-item>
          <q-item v-if="authStore.isAdmin" class="text-foreground" clickable :to="'/records'" dense>
            <q-item-section avatar>
              <q-icon name="fa-brands fa-wpforms" size="xs" />
            </q-item-section>
            <q-item-section>
              <q-item-label header class="text-foreground text-weight-medium q-pl-sm q-py-sm">{{
                t('records')
              }}</q-item-label>
            </q-item-section>
          </q-item>
          <q-item-label
            v-if="authStore.isAdmin"
            class="text-caption text-weight-bold text-foreground q-mt-xs q-pb-xs"
            header
          >
            {{ t('administration') }}
          </q-item-label>
          <q-item v-if="authStore.isAdmin" class="text-foreground" clickable :to="'/users'" dense>
            <q-item-section avatar>
              <q-icon name="fa-solid fa-users" size="xs" />
            </q-item-section>
            <q-item-section>
              <q-item-label header class="text-foreground text-weight-medium q-pl-sm q-py-sm">{{
                t('users')
              }}</q-item-label>
            </q-item-section>
          </q-item>
          <q-item-label
            class="text-caption text-weight-bold text-foreground q-mt-xs q-pb-xs"
            header
            >{{ t('help') }}</q-item-label
          >
          <q-item class="text-foreground" clickable :to="'/doc'" dense>
            <q-item-section avatar>
              <q-icon name="fa-solid fa-book" size="xs" />
            </q-item-section>
            <q-item-section>
              <q-item-label header class="text-foreground text-weight-medium q-pl-sm q-py-sm">{{
                t('doc')
              }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>

        <q-space />

        <!-- dark mode is temporarily disabled
        <q-toggle
          :model-value="$q.dark.isActive"
          @update:model-value="(e) => $q.dark.set(e)"
          :label="t('dark_mode')"
        />
        -->

        <div v-if="authStore.isAuthenticated" class="q-pa-sm">
          <div class="username-line">
            <q-avatar size="60px" icon="fa-solid fa-user" />
            <div>
              <div class="text-body1">{{ username }}</div>
              <div class="actions-bar">
                <q-chip color="foreground" text-color="white" class="q-ma-none">{{
                  authStore.isAdmin ? t('role.platyp-admin') : t('role.platyp-user')
                }}</q-chip>
                <q-btn
                  color="foreground"
                  size="sm"
                  icon="fa-solid fa-right-from-bracket"
                  class="auth-button"
                  @click="onLogout"
                >
                  {{ t('signout') }}
                </q-btn>
              </div>
            </div>
          </div>
        </div>
      </div>
    </q-drawer>

    <q-page-container v-if="authStore.isAuthenticated">
      <div class="background-container">
        <img
          :src="$q.dark.isActive ? '/admin/PATTERN-BLANC.svg' : '/admin/PATTERN-VIOLET.svg'"
          aria-hidden="true"
          class="background-pattern"
        />
      </div>
      <router-view />
    </q-page-container>

    <app-footer />
  </q-layout>
</template>

<script setup lang="ts">
import AppFooter from '@/components/AppFooter.vue'
import { Cookies, useQuasar } from 'quasar'
import { locales } from '@/boot/i18n'

const authStore = useAuthStore()
const { locale, t } = useI18n()
const router = useRouter()
const $q = useQuasar()

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
  authStore.logout()
}

function onLocaleSelection(localeOpt: { label: string; value: string }) {
  locale.value = localeOpt.value
  Cookies.set('locale', localeOpt.value)
}
</script>

<style scoped>
.logos {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
}

.background-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;

  pointer-events: none;
  z-index: -1;
}

.background-pattern {
  position: absolute;

  top: -10rem;
  left: 15rem;
  width: 100rem;
  height: 200rem;

  object-fit: contain;
  rotate: -40deg;

  opacity: 0.05;
}

.nav-wrapper {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  height: 100%;
}

:deep(.nav-list .q-item__section--avatar) {
  padding-right: 0;
  min-width: 24px;
}

.username-line {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

:deep(.auth-button .q-btn__content) {
  gap: 0.5rem;
  font-size: 0.65rem;
}

.actions-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  justify-content: space-between;
}
</style>
