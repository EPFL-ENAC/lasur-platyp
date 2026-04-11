<template>
  <q-layout view="hHh lpR fFf">
    <q-header bordered class="bg-nav">
      <q-toolbar>
        <a href="https://modus-ge.ch/" target="_blank">
          <img
            :src="$q.dark.isActive ? '/LOGO-JAUNE.svg' : '/LOGO-VIOLET.svg'"
            alt="Logo"
            height="25px"
          />
        </a>

        <q-space />

        <q-btn-dropdown flat dense color="foreground" :label="locale" class="text-bold on-left">
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

        <q-toggle
          :model-value="$q.dark.isActive"
          color="foreground"
          keep-color
          @update:model-value="(e) => $q.dark.set(e)"
          :label="t('dark_mode')"
          class="q-mr-md text-foreground"
        />

        <a href="https://www.epfl.ch/labs/lasur/" target="_blank" class="q-mt-sm">
          <img src="/EPFL.svg" height="20px" style="filter: grayscale(100%); opacity: 0.8" />
        </a>
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
import { locales, t } from 'boot/i18n'

const { locale } = useI18n()
const $q = useQuasar()

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
</script>

<style scoped>
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
