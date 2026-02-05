<template>
  <q-page>
    <div class="text-h5 q-pa-md">{{ t('doc') }}</div>
    <q-separator />
    <div class="q-pa-md">
      <q-markdown
        :src="locale === 'fr' ? WelcomeFr : WelcomeEn"
        no-heading-anchor-links
        class="q-mb-xl"
      />
      <div>
        <q-list v-for="entry in entries" :key="entry.title" bordered class="bg-grey-3 q-mb-md">
          <q-expansion-item expand-separator :label="entry.title" :caption="entry.caption">
            <q-card>
              <q-card-section>
                <q-markdown v-if="entry.markdown" :src="entry.markdown" no-heading-anchor-links />
              </q-card-section>
            </q-card>
          </q-expansion-item>
        </q-list>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import WelcomeEn from 'src/assets/docs/en/welcome.md'
import WelcomeFr from 'src/assets/docs/fr/welcome.md'
import CompanyProfileEn from 'src/assets/docs/en/company_profile.md'
import CompanyProfileFr from 'src/assets/docs/fr/company_profile.md'
import CampaignManagementEn from 'src/assets/docs/en/campaign_management.md'
import CampaignManagementFr from 'src/assets/docs/fr/campaign_management.md'
import ParticipantsManagementEn from 'src/assets/docs/en/participants_management.md'
import ParticipantsManagementFr from 'src/assets/docs/fr/participants_management.md'

const { locale, t } = useI18n()

const entries = computed(() => [
  {
    title: t('docs.company_profile.title'),
    caption: t('docs.company_profile.caption'),
    markdown: locale.value === 'fr' ? CompanyProfileFr : CompanyProfileEn,
  },
  {
    title: t('docs.campaign_management.title'),
    caption: t('docs.campaign_management.caption'),
    markdown: locale.value === 'fr' ? CampaignManagementFr : CampaignManagementEn,
  },
  {
    title: t('docs.participants_management.title'),
    caption: t('docs.participants_management.caption'),
    markdown: locale.value === 'fr' ? ParticipantsManagementFr : ParticipantsManagementEn,
  },
])
</script>
