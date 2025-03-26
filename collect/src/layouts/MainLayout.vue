<template>
  <q-layout view="hHh lpR fFf">
    <q-header bordered class="bg-primary text-white">
      <q-toolbar>
        <a href="https://modus-ge.ch/" target="_blank">
          <img src="/modus.svg" height="25px" />
        </a>
        <q-toolbar-title class="text-white text-bold text-center">
          <span>{{ t('main.brand') }}</span>
        </q-toolbar-title>

        <q-btn-dropdown flat dense :label="locale" class="text-bold on-left">
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
        <a href="https://www.epfl.ch/labs/lasur/" target="_blank" class="q-mt-sm">
          <img src="/EPFL.svg" height="20px" style="filter: grayscale(100%); opacity: 0.8" />
        </a>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { Cookies } from 'quasar'
import { locales } from 'boot/i18n'

const { locale, t } = useI18n()

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
