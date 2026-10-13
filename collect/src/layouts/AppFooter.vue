<template>
  <q-footer class="app-footer">
    <div class="app-footer__content">
      <div class="app-footer__col">
        <a :href="t('main.links.website')" target="_blank" rel="noopener">
          <img
            :src="$q.dark.isActive ? '/branding/logo-dark.svg' : '/branding/logo.svg'"
            :alt="t('main.brand')"
            class="app-footer__brand"
          />
        </a>
      </div>
      <div v-for="partner in branding.partners" :key="partner.url" class="app-footer__col">
        <a :href="partner.url" target="_blank" rel="noopener" class="app-footer__logo-link">
          <span
            class="app-footer__logo"
            role="img"
            :aria-label="partner.alt"
            :style="{ width: `${partner.width}px`, '--logo': `url('${partner.logo}')` }"
          />
        </a>
        <p v-if="partner.name" class="app-footer__name">{{ t(partner.name) }}</p>
        <a
          v-for="link in partner.links"
          :key="link.url"
          :href="link.url"
          target="_blank"
          rel="noopener"
          class="app-footer__link"
        >
          {{ t(link.label) }}
          <q-icon name="arrow_outward" />
        </a>
      </div>
    </div>
  </q-footer>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar'
import { t } from '@/boot/i18n'
import { branding } from '@/utils/branding'

const $q = useQuasar()
</script>

<style scoped lang="scss">
.app-footer {
  --footer-bg: #{$brand-primary-100};
  --footer-fg: #{$brand-secondary-800};
  --footer-link: #{$brand-primary-700};

  background-color: var(--footer-bg);
  color: var(--footer-fg);
  padding: 48px 0;
}

.body--dark .app-footer {
  --footer-bg: #{$brand-secondary-700};
  --footer-fg: #{$brand-secondary-50};
  --footer-link: #{$brand-primary-300};
}

// Same container as the header toolbar, so both bands align on the same edges.
.app-footer__content {
  display: grid;
  grid-template-columns: 1fr;
  grid-auto-columns: auto;
  grid-auto-flow: column;
  column-gap: 64px;
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
  height: 32px;
  -webkit-mask-image: var(--logo);
  mask-image: var(--logo);
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
    grid-auto-flow: row;
    gap: 32px;
  }
}
</style>
