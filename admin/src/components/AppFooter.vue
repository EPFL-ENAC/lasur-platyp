<template>
  <q-footer class="app-footer">
    <div class="app-footer__content">
      <div class="app-footer__col">
        <a href="https://modus-ge.ch/" target="_blank" rel="noopener">
          <img src="/admin/LOGO-JAUNE.svg" alt="Mobilyse" class="app-footer__brand" />
        </a>
      </div>

      <div class="app-footer__col">
        <a href="https://modus-ge.ch/" target="_blank" rel="noopener" class="app-footer__logo-link">
          <span class="app-footer__logo app-footer__logo--modus" role="img" aria-label="Modus" />
        </a>
        <p class="app-footer__name">{{ t('footer.modus_name') }}</p>
        <a href="https://modus-ge.ch/" target="_blank" rel="noopener" class="app-footer__link">
          {{ t('footer.modus_tagline') }}
          <q-icon name="arrow_outward" />
        </a>
      </div>

      <div class="app-footer__col">
        <a href="https://www.epfl.ch" target="_blank" rel="noopener" class="app-footer__logo-link">
          <span class="app-footer__logo app-footer__logo--epfl" role="img" aria-label="EPFL" />
        </a>
        <a
          href="https://www.epfl.ch/labs/lasur/"
          target="_blank"
          rel="noopener"
          class="app-footer__link"
        >
          {{ t('footer.lasur') }}
          <q-icon name="arrow_outward" />
        </a>
        <a
          href="https://www.epfl.ch/schools/enac/about/data-at-enac/enac-it4research/"
          target="_blank"
          rel="noopener"
          class="app-footer__link"
        >
          {{ t('footer.it4r') }}
          <q-icon name="arrow_outward" />
        </a>
      </div>
    </div>
  </q-footer>
</template>

<script setup lang="ts">
const { t } = useI18n()
</script>

<style scoped lang="scss">
// Always the dark band, whatever the theme
.app-footer {
  --footer-bg: #{$brand-purple-700};
  --footer-fg: #{$brand-purple-50};
  --footer-link: #{$brand-yellow-300};

  background-color: var(--footer-bg);
  color: var(--footer-fg);
  padding: 48px 0;
}

.app-footer__content {
  display: grid;
  grid-template-columns: 30% 44% 26%;
  align-items: start;
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 12px;
}

.app-footer__col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
}

.app-footer__brand {
  height: 32px;
}

.app-footer__logo-link {
  display: block;
  color: inherit;
  margin-bottom: 4px;
}

// The partner logos ship as single-colour (white) artwork, so they are painted
// through a mask instead of being loaded as images: the fill then follows the
// footer foreground and flips with the theme from one asset.
.app-footer__logo {
  display: block;
  background-color: currentColor;

  -webkit-mask-repeat: no-repeat;
  mask-repeat: no-repeat;
  -webkit-mask-position: left center;
  mask-position: left center;
  -webkit-mask-size: contain;
  mask-size: contain;
}

.app-footer__logo--modus {
  width: 88px;
  height: 32px;
  -webkit-mask-image: url('/admin/modus_logo.svg');
  mask-image: url('/admin/modus_logo.svg');
}

.app-footer__logo--epfl {
  width: 110px;
  height: 32px;
  -webkit-mask-image: url('/admin/epfl_logo.svg');
  mask-image: url('/admin/epfl_logo.svg');
}

.app-footer__name {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  line-height: 20px;
  color: var(--footer-fg);
}

.app-footer__link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  line-height: 20px;
  color: var(--footer-link);
}

.app-footer__link:hover {
  text-decoration: underline;
}

.app-footer__link .q-icon {
  font-size: 16px;
}

// Stack the columns once the three-up grid stops fitting.
@media (max-width: 767px) {
  .app-footer__content {
    grid-template-columns: 1fr;
    gap: 32px;
  }
}
</style>
