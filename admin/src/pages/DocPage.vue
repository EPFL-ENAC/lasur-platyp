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
                <div v-else>
                  {{ entry.content }}
                </div>
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

const { locale, t } = useI18n()

const entries = computed(() => [
  {
    title: 'How to manage my company profile',
    caption: 'Learn how to update your company information and settings',
    markdown: locale.value === 'fr' ? CompanyProfileFr : CompanyProfileEn,
  },
  {
    title: 'How to create a campaign',
    caption: 'Learn the basics of creating and managing campaigns',
    markdown: locale.value === 'fr' ? CampaignManagementFr : CampaignManagementEn,
  },
  {
    title: 'How to manage participants',
    caption: 'A guide to adding, editing, and removing participants',
    content:
      'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quidem, eius reprehenderit eos corrupti commodi magni quaerat ex numquam, dolorum officiis modi facere maiores architecto suscipit iste eveniet doloribus ullam aliquid.',
  },
  {
    title: 'How to analyze results',
    caption: 'Understanding the records and insights from your campaigns',
    content:
      'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quidem, eius reprehenderit eos corrupti commodi magni quaerat ex numquam, dolorum officiis modi facere maiores architecto suscipit iste eveniet doloribus ullam aliquid.',
  },
])
</script>
