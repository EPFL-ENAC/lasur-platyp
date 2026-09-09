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
          <q-item class="nav-item" clickable :to="'/'" exact>
            <q-item-section avatar>
              <q-icon name="grid_view" />
            </q-item-section>
            <q-item-section>{{ t('dashboard') }}</q-item-section>
          </q-item>

          <div class="nav-section">{{ t('content') }}</div>
          <q-item class="nav-item" clickable :to="'/companies'">
            <q-item-section avatar>
              <q-icon name="fa-regular fa-building" />
            </q-item-section>
            <q-item-section>{{ t('companies') }}</q-item-section>
            <q-item-section v-if="countsStore.companies !== undefined" side>
              <span class="nav-badge">{{ formatCount(countsStore.companies) }}</span>
            </q-item-section>
          </q-item>
          <q-item v-if="authStore.isAdmin" class="nav-item" clickable :to="'/records'">
            <q-item-section avatar>
              <q-icon name="fa-regular fa-rectangle-list" />
            </q-item-section>
            <q-item-section>{{ t('records') }}</q-item-section>
            <q-item-section v-if="countsStore.records !== undefined" side>
              <span class="nav-badge">{{ formatCount(countsStore.records) }}</span>
            </q-item-section>
          </q-item>

          <template v-if="authStore.isAdmin">
            <div class="nav-section">{{ t('administration') }}</div>
            <q-item class="nav-item" clickable :to="'/users'">
              <q-item-section avatar>
                <q-icon name="fa-solid fa-user-group" />
              </q-item-section>
              <q-item-section>{{ t('users') }}</q-item-section>
              <q-item-section v-if="countsStore.users !== undefined" side>
                <span class="nav-badge">{{ formatCount(countsStore.users) }}</span>
              </q-item-section>
            </q-item>
          </template>
        </q-list>

        <q-space />

        <!-- dark mode is temporarily disabled
        <q-toggle
          :model-value="$q.dark.isActive"
          @update:model-value="(e) => $q.dark.set(e)"
          :label="t('dark_mode')"
        />
        -->

        <q-list class="nav-list nav-list--utility">
          <q-item class="nav-item" clickable :to="'/doc'">
            <q-item-section avatar>
              <q-icon name="fa-regular fa-file-lines" />
            </q-item-section>
            <q-item-section>{{ t('doc') }}</q-item-section>
            <q-item-section side>
              <q-icon name="arrow_outward" class="nav-item__link-icon" />
            </q-item-section>
          </q-item>
        </q-list>

        <div v-if="authStore.isAuthenticated" class="nav-account">
          <q-btn flat no-caps align="left" class="nav-account__btn">
            <q-avatar size="36px" class="nav-account__avatar">{{ initials }}</q-avatar>
            <div class="nav-account__text">
              <div class="nav-account__name" :title="displayName">{{ displayName }}</div>
              <div class="nav-account__role">
                {{ authStore.isAdmin ? t('role.platyp-admin') : t('role.platyp-user') }}
              </div>
            </div>
            <q-icon name="unfold_more" class="nav-account__chevron" />
            <q-menu anchor="top middle" self="bottom middle" :offset="[0, 8]">
              <q-list>
                <q-item clickable v-close-popup @click="onLogout">
                  <q-item-section avatar>
                    <q-icon name="logout" size="18px" />
                  </q-item-section>
                  <q-item-section>{{ t('signout') }}</q-item-section>
                </q-item>
              </q-list>
            </q-menu>
          </q-btn>
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
const countsStore = useCountsStore()
const { locale, t } = useI18n()
const router = useRouter()
const $q = useQuasar()

const drawerOpen = ref(false)

const displayName = computed(() => authStore.profile?.email || '')

const initials = computed(() => {
  const p = authStore.profile
  const letters = [p?.firstName, p?.lastName].filter(Boolean).map((n) => n![0])
  if (letters.length) return letters.join('').toUpperCase()
  return (p?.email || '?')[0]!.toUpperCase()
})
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
    } else {
      countsStore.refresh()
    }
  })
})

// Badges reflect the tables at the moment the menu opens
watch(drawerOpen, (open) => {
  if (open) countsStore.refresh()
})

const compactNumber = computed(
  () => new Intl.NumberFormat(locale.value, { notation: 'compact', maximumFractionDigits: 1 }),
)

function formatCount(n: number): string {
  return compactNumber.value.format(n)
}

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

// Page content: 96px margins on desktop, back to the page default below
.q-page-container :deep(.q-page) {
  padding: 96px;
}

@media (max-width: 1023px) {
  .q-page-container :deep(.q-page) {
    padding: 24px;
  }
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

.nav-list {
  padding: 24px 12px 0;
}

.nav-list--utility {
  padding: 0 12px 12px;
}

// Section headers: small caps, muted, tight
.nav-section {
  margin: 20px 12px 6px;
  font-size: 11px;
  font-weight: 700;
  line-height: 16px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: $brand-purple-400;
}

// Rows: 40px, 14px labels, 18px icons. Inactive icons are muted, the active
// row carries full-weight ink and a 3px accent bar on a soft white pill.
.nav-item {
  position: relative;
  min-height: 40px;
  padding: 0 12px;
  border-radius: 8px; // radius-default
  font-size: 14px;
  font-weight: 600;
  line-height: 20px;
  color: $brand-purple-800;
}

.nav-item + .nav-item {
  margin-top: 2px;
}

.nav-item :deep(.q-item__section--avatar) {
  min-width: 20px;
  padding-right: 12px; // spacing-md
  color: $brand-purple-400;
}

.nav-item :deep(.q-icon) {
  font-size: 18px;
}

.nav-item:hover {
  background-color: $brand-yellow-200;
}

.nav-item.q-router-link--active,
.nav-item.q-router-link--active:hover {
  background-color: $brand-yellow-25;
}

.nav-item.q-router-link--active::before {
  content: '';
  position: absolute;
  top: 8px;
  bottom: 8px;
  left: 0;
  width: 3px;
  border-radius: 0 3px 3px 0;
  background-color: $brand-purple-800;
}

.nav-item.q-router-link--active :deep(.q-item__section--avatar) {
  color: $brand-purple-800;
}

.nav-item :deep(.q-item__section--side) {
  padding-left: 8px;
}

.nav-item :deep(.nav-item__link-icon) {
  font-size: 16px;
  color: $brand-purple-400;
}

// Count badge, the total of the table on that page
.nav-badge {
  display: inline-block;
  min-width: 24px;
  padding: 0 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  line-height: 20px;
  text-align: center;
  color: $brand-purple-700;
  background-color: rgba($brand-purple-800, 0.08);
}

// Account row: avatar, name, role. Sign-out lives in the menu it opens.
.nav-account {
  padding: 12px;
  border-top: 1px solid $brand-purple-100;
}

.q-btn.nav-account__btn {
  width: 100%;
  padding: 6px 8px;
  border-radius: 8px; // radius-default
  color: $brand-purple-800;
}

.q-btn.nav-account__btn :deep(.q-btn__content) {
  flex-wrap: nowrap;
  gap: 12px; // spacing-md
  width: 100%;
}

.nav-account__avatar {
  flex: none;
  background-color: $brand-purple-800;
  color: $brand-yellow-100;
  font-size: 13px;
  font-weight: 700;
}

.nav-account__text {
  flex: 1;
  min-width: 0;
  text-align: left;
}

.nav-account__name {
  font-size: 14px;
  font-weight: 600;
  line-height: 20px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-account__role {
  font-size: 12px;
  font-weight: 400;
  line-height: 16px;
  color: $brand-purple-400;
}

.nav-account__chevron {
  flex: none;
  font-size: 18px;
  color: $brand-purple-400;
}

// Dark theme
.body--dark .nav-section,
.body--dark .nav-item :deep(.q-item__section--avatar),
.body--dark .nav-account__role,
.body--dark .nav-account__chevron {
  color: $brand-purple-200;
}

.body--dark .nav-item,
.body--dark .q-btn.nav-account__btn {
  color: $brand-purple-50;
}

.body--dark .nav-item:hover {
  background-color: rgba($brand-purple-50, 0.08);
}

.body--dark .nav-item.q-router-link--active,
.body--dark .nav-item.q-router-link--active:hover {
  background-color: $brand-purple-600;
}

.body--dark .nav-item.q-router-link--active::before {
  background-color: $brand-yellow-200;
}

.body--dark .nav-item.q-router-link--active :deep(.q-item__section--avatar) {
  color: $brand-yellow-200;
}

.body--dark .nav-account {
  border-top-color: $brand-purple-600;
}

.body--dark .nav-account__avatar {
  background-color: $brand-yellow-200;
  color: $brand-purple-800;
}

.body--dark .nav-badge {
  color: $brand-purple-50;
  background-color: rgba($brand-purple-50, 0.12);
}

</style>
