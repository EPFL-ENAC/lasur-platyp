<template>
  <q-layout view="hHh LpR lfr">
    <q-header v-if="authStore.isAuthenticated" bordered class="bg-nav">
      <q-toolbar class="header-toolbar">
        <q-toolbar-title class="logos">
          <a href="https://modus-ge.ch/" target="_blank" class="logo" rel="noopener noreferrer">
            <img
              :src="$q.dark.isActive ? '/admin/LOGO-JAUNE.svg' : '/admin/LOGO-VIOLET.svg'"
              height="32px"
            />
          </a>
        </q-toolbar-title>

        <q-btn-dropdown
          flat
          no-caps
          dropdown-icon="expand_more"
          :label="currentLocaleLabel"
          class="header-btn on-left"
        >
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

        <q-btn flat round class="menu-btn" aria-label="Menu" @click="toggleDrawer">
          <svg
            class="menu-btn__icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.2"
            stroke-linecap="round"
            aria-hidden="true"
          >
            <line x1="2" y1="5" x2="22" y2="5" />
            <line x1="2" y1="12" x2="15" y2="12" />
            <line x1="2" y1="19" x2="22" y2="19" />
          </svg>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-if="authStore.isAuthenticated"
      v-model="drawerOpen"
      side="left"
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

        <div class="nav-logos">
          <a href="https://modus-ge.ch/" target="_blank" rel="noopener" class="nav-logos__link">
            <span class="nav-logos__logo nav-logos__logo--modus" role="img" aria-label="Modus" />
          </a>
          <a href="https://www.epfl.ch" target="_blank" rel="noopener" class="nav-logos__link">
            <span class="nav-logos__logo nav-logos__logo--epfl" role="img" aria-label="EPFL" />
          </a>
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
import { locales, localeLabel } from '@/boot/i18n'

const authStore = useAuthStore()
const { locale, t } = useI18n()
const router = useRouter()
const $q = useQuasar()

const drawerOpen = ref(false)

const username = computed(() => authStore.profile?.email)
const localeOptions = computed(() => {
  return locales.map((key) => ({
    label: localeLabel(key),
    value: key,
  }))
})

const currentLocaleLabel = computed(() => localeLabel(locale.value))

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

function toggleDrawer() {
  drawerOpen.value = !drawerOpen.value
}

function onLogout() {
  authStore.logout()
}

function onLocaleSelection(localeOpt: { label: string; value: string }) {
  locale.value = localeOpt.value
  Cookies.set('locale', localeOpt.value)
}
</script>

<style scoped lang="scss">
// Fixed header height, same as collect
.header-toolbar {
  height: 64px;
  min-height: 64px;
}

// Header controls, same skin as the collect app header
.q-btn.header-btn {
  --header-btn-bg: #{'white'};
  --header-btn-border: #{$brand-purple-100};
  --header-btn-text: #{$brand-purple-800};
  --header-btn-shadow: 0 1px 2px 0 rgba(10, 13, 18, 0.05), inset 0 -2px 0 0 rgba(10, 13, 18, 0.05);

  height: 48px;
  min-height: 48px;
  padding: 10px 14px !important;
  border: 1px solid var(--header-btn-border);
  border-radius: 8px; // radius-default
  background-color: var(--header-btn-bg) !important;
  color: var(--header-btn-text) !important;
  box-shadow: var(--header-btn-shadow);
}

.body--dark .q-btn.header-btn {
  --header-btn-bg: #{$brand-purple-800};
  --header-btn-border: #{$brand-purple-200};
  --header-btn-text: #{$brand-purple-50};
}

.q-btn.header-btn :deep(.q-btn-dropdown__arrow) {
  margin-left: 4px; // spacing-xs
  font-size: 20px;
}

// Burger: plain icon, no button skin
.q-btn.menu-btn {
  width: 48px;
  height: 48px;
  color: $brand-purple-800;
}

.body--dark .q-btn.menu-btn {
  color: $brand-purple-50;
}

.menu-btn__icon {
  width: 24px;
  height: 24px;
}

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

// Partner logos strip at the bottom of the menu: violet band, light yellow
// artwork. The logos ship as single-colour artwork and are painted through a
// mask so one asset takes any fill colour.
.nav-logos {
  display: flex;
  align-items: center;
  gap: 24px; // spacing-xl
  padding: 20px 16px;
  background-color: $brand-purple-700;
  color: $brand-yellow-100;
}

.nav-logos__link {
  display: block;
  color: inherit;
  opacity: 0.9;
}

.nav-logos__link:hover {
  opacity: 1;
}

.nav-logos__logo {
  display: block;
  background-color: currentColor;

  -webkit-mask-repeat: no-repeat;
  mask-repeat: no-repeat;
  -webkit-mask-position: left center;
  mask-position: left center;
  -webkit-mask-size: contain;
  mask-size: contain;
}

.nav-logos__logo--modus {
  width: 72px;
  height: 22px;
  -webkit-mask-image: url('/admin/modus.svg');
  mask-image: url('/admin/modus.svg');
}

.nav-logos__logo--epfl {
  width: 76px;
  height: 22px;
  -webkit-mask-image: url('/admin/epfl_logo.svg');
  mask-image: url('/admin/epfl_logo.svg');
}
</style>
