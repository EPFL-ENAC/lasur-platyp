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
        <a href="https://www.epfl.ch/labs/lasur/" target="_blank" class="q-mt-sm">
          <img src="/EPFL.svg" height="20px" style="filter: grayscale(100%)" />
        </a>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
const { t } = useI18n()
</script>
