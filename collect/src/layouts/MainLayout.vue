<template>
  <q-layout view="hHh lpR fFf">
    <q-header bordered class="bg-primary text-white">
      <q-toolbar>
        <q-btn dense flat round icon="menu" @click="toggleLeftDrawer" />

        <q-toolbar-title>
          <a href="https://modus-ge.ch/" target="_blank">
            <img src="/modus.svg" height="25px" />
          </a>
          <span class="text-white text-bold on-right">{{ t('main.brand') }}</span>
        </q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" side="left" behavior="mobile" bordered>
      <q-list>
        <q-item-label header> Essential Links </q-item-label>

        <EssentialLink v-for="link in linksList" :key="link.title" v-bind="link" />
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import EssentialLink, { type EssentialLinkProps } from 'components/EssentialLink.vue'

const { t } = useI18n()

const linksList: EssentialLinkProps[] = [
  {
    title: 'Modus',
    caption: 'modus-ge.ch',
    icon: 'record_voice_over',
    link: 'https://modus-ge.ch/',
  },
  {
    title: 'EPFL LASUR',
    caption: 'epfl.ch/lasur',
    icon: 'school',
    link: 'https://www.epfl.ch/labs/lasur/',
  },
]

const leftDrawerOpen = ref(false)

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value
}
</script>
