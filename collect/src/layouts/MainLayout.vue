<template>
  <q-layout view="hHh lpR fFf">
    <q-header bordered class="bg-nav">
      <q-toolbar class="header-toolbar">
        <div class="header-toolbar__content">
          <a href="https://modus-ge.ch/" target="_blank">
            <img
              :src="$q.dark.isActive ? '/LOGO-JAUNE.svg' : '/LOGO-VIOLET.svg'"
              alt="Logo"
              height="25px"
            />
          </a>

          <q-space />

          <q-btn
            flat
            class="header-btn header-btn--icon on-left"
            :icon="$q.dark.isActive ? 'light_mode' : 'dark_mode'"
            :aria-label="t('dark_mode')"
            @click="$q.dark.toggle()"
          />

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
        </div>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <div class="background-container">
        <img
          :src="$q.dark.isActive ? '/PATTERN-BLANC.svg' : '/PATTERN-VIOLET.svg'"
          aria-hidden="true"
          class="background-pattern"
        />
      </div>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { Cookies, useQuasar } from 'quasar'
import { locales, t } from '@/boot/i18n'

const { locale } = useI18n()
const $q = useQuasar()

const localeLabels: Record<string, string> = {
  en: 'English',
  fr: 'Français',
}

const localeOptions = computed(() => {
  return locales.map((key) => ({
    label: localeLabels[key] ?? key.toUpperCase(),
    value: key,
  }))
})

const currentLocaleLabel = computed(() => localeLabels[locale.value] ?? locale.value.toUpperCase())

function onLocaleSelection(localeOpt: { label: string; value: string }) {
  locale.value = localeOpt.value
  Cookies.set('locale', localeOpt.value)
}
</script>

<style scoped lang="scss">
// Fixed header height
.header-toolbar {
  height: 64px;
  min-height: 64px;
  padding: 0;
}

// Keep the toolbar bar full width, but constrain its content
.header-toolbar__content {
  display: flex;
  align-items: center;
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 12px; // q-toolbar default gutter
}

.q-btn.header-btn {
  --header-btn-bg: #{'white'};
  --header-btn-border: #{$brand-purple-100};
  --header-btn-text: #{$brand-purple-800};
  --header-btn-icon: #{$brand-purple-400};
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

// Icon-only variant
.q-btn.header-btn--icon {
  width: 48px;
  min-width: 48px;
  height: 48px;
  padding: 10px !important;
  border-radius: 8px; // radius-md
}

.q-btn.header-btn--icon :deep(.q-icon) {
  font-size: 20px;
  color: var(--header-btn-icon);
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
  left: -5rem;
  width: 100rem;
  height: 200rem;

  object-fit: contain;
  rotate: -40deg;

  opacity: 0.05;
}
</style>
