<template>
  <q-footer class="footer q-py-lg q-px-xl bg-secondary">
    <div>
      <img src="/admin/LOGO-JAUNE.svg" alt="Mobilyse">
      <q-markdown :src="t('footer.mobilyse')" />
    </div>
    <div>
      <img src="/admin/modus.svg" alt="Modus">
      <q-markdown :src="t('footer.modus')" />
    </div>
    <div>
      <img src="/admin/EPFL.svg" alt="EPFL">
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
</style>
