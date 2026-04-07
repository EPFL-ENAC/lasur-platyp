<template>
  <q-layout view="hHh LpR fFf">
    <q-header v-if="authStore.isAuthenticated" bordered class="bg-nav text-grey-10">
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
            <img :src="$q.dark.isActive ? 'LOGO-JAUNE.svg' : 'LOGO-VIOLET.svg'" height="32px" />
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
          <img src="EPFL.svg" height="20px" class="on-left" />
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
          <q-item clickable :to="'/'" exact>
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
              <q-icon name="fa-solid fa-building" size="sm" />
            </q-item-section>
            <q-item-section>
              <q-item-label header>{{ t('companies') }}</q-item-label>
            </q-item-section>
          </q-item>
          <q-item v-if="authStore.isAdmin" clickable :to="'/records'">
            <q-item-section avatar>
              <q-icon name="fa-brands fa-wpforms" size="sm" />
            </q-item-section>
            <q-item-section>
              <q-item-label header>{{ t('records') }}</q-item-label>
            </q-item-section>
          </q-item>
          <q-item-label v-if="authStore.isAdmin" class="text-h6" header>
            {{ t('administration') }}
          </q-item-label>
          <q-item v-if="authStore.isAdmin" clickable :to="'/users'">
            <q-item-section avatar>
              <q-icon name="fa-solid fa-users" size="sm" />
            </q-item-section>
            <q-item-section>
              <q-item-label header>{{ t('users') }}</q-item-label>
            </q-item-section>
          </q-item>
          <q-item-label class="text-h6" header>{{ t('help') }}</q-item-label>
          <q-item clickable :to="'/doc'">
            <q-item-section avatar>
              <q-icon name="fa-solid fa-book" size="sm" />
            </q-item-section>
            <q-item-section>
              <q-item-label header>{{ t('doc') }}</q-item-label>
            </q-item-section>
          </q-item>
          <q-item clickable :to="'/legal-notice'">
            <q-item-section avatar>
              <q-icon name="fa-solid fa-gavel" size="sm" />
            </q-item-section>
            <q-item-section>
              <q-item-label header>{{ t('legal_notice') }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>

        <q-space />

        <q-toggle
          :model-value="$q.dark.isActive"
          @update:model-value="(e) => $q.dark.set(e)"
          :label="t('dark_mode')"
        />

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
          :src="$q.dark.isActive ? 'PATTERN-BLANC.svg' : 'PATTERN-VIOLET.svg'"
          aria-hidden="true"
          class="background-pattern"
        />
      </div>
      <router-view />
    </q-page-container>

    <q-dialog v-if="authStore.isAuthenticated" v-model="showDataProtectionNotice">
      <q-card>
        <q-card-section>
          <div class="text-h6">{{ t('data_protection_notice.title') }}</div>
        </q-card-section>

        <q-card-section class="q-py-none">
          <q-markdown :src="t('data_protection_notice.content')" no-heading-anchor-links />
        </q-card-section>

        <q-card-actions>
          <q-toggle v-model="dataProtection.doNotShowNotice" :label="t('do_not_show_again')" />
        </q-card-actions>

        <q-card-actions align="right">
          <q-btn flat :label="t('close')" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-layout>
</template>

<script setup lang="ts">
import { Cookies, useQuasar } from 'quasar'
import { locales } from 'boot/i18n'

const dataProtection = useDataProtectionStore()
const authStore = useAuthStore()
const { locale, t } = useI18n()
const router = useRouter()
const $q = useQuasar()

const leftDrawerOpen = ref(false)
const showDataProtectionNotice = ref(!dataProtection.doNotShowNotice)

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

:deep(.nav-list .q-item__label--header) {
  color: var(--q-color-secondary);
  font-size: 1rem;
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
