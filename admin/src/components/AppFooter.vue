<template>
  <q-footer class="footer q-py-lg q-px-xl bg-secondary">
    <div>
      <a href="https://modus-ge.ch/project/toolkit-mobilite" target="_blank" rel="noopener noreferrer">
        <img src="/admin/LOGO-JAUNE.svg" alt="Mobilyse" />
      </a>
    </div>
    <div>
      <a href="http://modus-ge.ch" target="_blank" rel="noopener noreferrer">
        <img src="/admin/powered_by_modus.svg" alt="Modus" />
      </a>
      <q-markdown :src="t('footer.modus')" />
    </div>
    <div>
      <a href="http://epfl.ch" target="_blank" rel="noopener noreferrer"><img src="/admin/EPFL.svg" alt="EPFL" /></a>
      <q-markdown :src="t('footer.epfl')" />
    </div>
  </q-footer>
</template>

<script setup lang="ts">
const { t } = useI18n()
</script>

<style scoped>
.footer {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
}
.footer > div {
  display: flex;
  flex-direction: column;
  align-items: start;
}
.footer img {
  height: 2rem;
  margin-bottom: 1rem;
}

:deep(a) {
  color: var(--q-primary) !important;
}
</style>
