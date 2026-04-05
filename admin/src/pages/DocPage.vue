<template>
  <q-page>
    <h4 class="text-h4 q-ma-none q-pa-md text-primary-dark">{{ t('doc') }}</h4>
    <q-separator />
    <div class="q-pa-md">
      <q-markdown
        :src="locale === 'fr' ? WelcomeFr : WelcomeEn"
        no-heading-anchor-links
        class="q-mb-xl"
      />
      <div>
        <div v-for="section in sections" :key="section.title" class="q-mb-md">
          <h6 class="text-h6 q-mb-xs">{{ section.title }}</h6>
          <p class="q-mb-md">{{ section.description ?? '' }}</p>

          <template v-for="entry in section.entries" :key="entry.title">
            <q-separator />

            <q-expansion-item
              switch-toggle-side
              :label="entry.title"
              :caption="entry.caption"
              class="bg-white"
              :content-inset-level="1"
              header-class="text-secondary"
            >
              <div class="q-pa-md">
                <q-markdown v-if="entry.markdown" :src="entry.markdown" no-heading-anchor-links />
              </div>
            </q-expansion-item>
          </template>
          <q-separator />
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import WelcomeEn from 'src/assets/docs/en/welcome.md'
import WelcomeFr from 'src/assets/docs/fr/welcome.md'
import CreateEn from 'src/assets/docs/en/organisations/create.md'
import CreateFr from 'src/assets/docs/fr/organisations/create.md'
import OrgSettingsEn from 'src/assets/docs/en/organisations/settings.md'
import OrgSettingsFr from 'src/assets/docs/fr/organisations/settings.md'
import EmployerMeasuresEn from 'src/assets/docs/en/organisations/employer_measures.md'
import EmployerMeasuresFr from 'src/assets/docs/fr/organisations/employer_measures.md'
import CustomMeasuresEn from 'src/assets/docs/en/organisations/custom_measures.md'
import CustomMeasuresFr from 'src/assets/docs/fr/organisations/custom_measures.md'
import BestPracticesEn from 'src/assets/docs/en/organisations/best_practices.md'
import BestPracticesFr from 'src/assets/docs/fr/organisations/best_practices.md'
import CommonIssuesEn from 'src/assets/docs/en/organisations/common_issues.md'
import CommonIssuesFr from 'src/assets/docs/fr/organisations/common_issues.md'
import CampaignSettingsEn from 'src/assets/docs/en/campaigns/settings.md'
import CampaignSettingsFr from 'src/assets/docs/fr/campaigns/settings.md'
import CampaignCommonIssuesEn from 'src/assets/docs/en/campaigns/common_issues.md'
import CampaignCommonIssuesFr from 'src/assets/docs/fr/campaigns/common_issues.md'
import CampaignBestPracticesEn from 'src/assets/docs/en/campaigns/best_practices.md'
import CampaignBestPracticesFr from 'src/assets/docs/fr/campaigns/best_practices.md'
import CampaignShareLinkEn from 'src/assets/docs/en/campaigns/share_link.md'
import CampaignShareLinkFr from 'src/assets/docs/fr/campaigns/share_link.md'
import CampaignIsochroneEn from 'src/assets/docs/en/campaigns/display_isochrone.md'
import CampaignIsochroneFr from 'src/assets/docs/fr/campaigns/display_isochrone.md'
import CampaignAnalyseResultsEn from 'src/assets/docs/en/campaigns/analyse_results.md'
import CampaignAnalyseResultsFr from 'src/assets/docs/fr/campaigns/analyse_results.md'
import CampaignRewardEn from 'src/assets/docs/en/campaigns/reward.md'
import CampaignRewardFr from 'src/assets/docs/fr/campaigns/reward.md'
import ParticipantsSettingsEn from 'src/assets/docs/en/participants/settings.md'
import ParticipantsSettingsFr from 'src/assets/docs/fr/participants/settings.md'
import ParticipantsCommonIssuesEn from 'src/assets/docs/en/participants/common_issues.md'
import ParticipantsCommonIssuesFr from 'src/assets/docs/fr/participants/common_issues.md'
import ParticipantsBestPracticesEn from 'src/assets/docs/en/participants/best_practices.md'
import ParticipantsBestPracticesFr from 'src/assets/docs/fr/participants/best_practices.md'

const { locale, t } = useI18n()

interface DocEntry {
  title: string
  caption: string
  markdown: string
}

interface DocSection {
  title: string
  description?: string
  entries: DocEntry[]
}

const sections = computed<DocSection[]>(() => [
  {
    title: t('docs.organisations.title'),
    entries: [
      {
        title: t('docs.organisations.create.title'),
        caption: t('docs.organisations.create.caption'),
        markdown: locale.value === 'fr' ? CreateFr : CreateEn,
      },
      {
        title: t('docs.organisations.settings.title'),
        caption: t('docs.organisations.settings.caption'),
        markdown: locale.value === 'fr' ? OrgSettingsFr : OrgSettingsEn,
      },
      {
        title: t('docs.organisations.employer_measures.title'),
        caption: t('docs.organisations.employer_measures.caption'),
        markdown: locale.value === 'fr' ? EmployerMeasuresFr : EmployerMeasuresEn,
      },
      {
        title: t('docs.organisations.custom_measures.title'),
        caption: t('docs.organisations.custom_measures.caption'),
        markdown: locale.value === 'fr' ? CustomMeasuresFr : CustomMeasuresEn,
      },
      {
        title: t('docs.organisations.common_issues.title'),
        caption: t('docs.organisations.common_issues.caption'),
        markdown: locale.value === 'fr' ? CommonIssuesFr : CommonIssuesEn,
      },
      {
        title: t('docs.organisations.best_practices.title'),
        caption: t('docs.organisations.best_practices.caption'),
        markdown: locale.value === 'fr' ? BestPracticesFr : BestPracticesEn,
      },
    ],
  },
  {
    title: t('docs.campaigns.title'),
    description: t('docs.campaigns.description'),
    entries: [
      {
        title: t('docs.campaigns.settings.title'),
        caption: t('docs.campaigns.settings.caption'),
        markdown: locale.value === 'fr' ? CampaignSettingsFr : CampaignSettingsEn,
      },
      {
        title: t('docs.campaigns.share_link.title'),
        caption: t('docs.campaigns.share_link.caption'),
        markdown: locale.value === 'fr' ? CampaignShareLinkFr : CampaignShareLinkEn,
      },
      {
        title: t('docs.campaigns.isochrone.title'),
        caption: t('docs.campaigns.isochrone.caption'),
        markdown: locale.value === 'fr' ? CampaignIsochroneFr : CampaignIsochroneEn,
      },
      {
        title: t('docs.campaigns.analyse_results.title'),
        caption: t('docs.campaigns.analyse_results.caption'),
        markdown: locale.value === 'fr' ? CampaignAnalyseResultsFr : CampaignAnalyseResultsEn,
      },
      {
        title: t('docs.campaigns.reward.title'),
        caption: t('docs.campaigns.reward.caption'),
        markdown: locale.value === 'fr' ? CampaignRewardFr : CampaignRewardEn,
      },
      {
        title: t('docs.campaigns.common_issues.title'),
        caption: t('docs.campaigns.common_issues.caption'),
        markdown: locale.value === 'fr' ? CampaignCommonIssuesFr : CampaignCommonIssuesEn,
      },
      {
        title: t('docs.campaigns.best_practices.title'),
        caption: t('docs.campaigns.best_practices.caption'),
        markdown: locale.value === 'fr' ? CampaignBestPracticesFr : CampaignBestPracticesEn,
      },
    ],
  },
  {
    title: t('docs.participants.title'),
    description: t('docs.participants.description'),
    entries: [
      {
        title: t('docs.participants.settings.title'),
        caption: t('docs.participants.settings.caption'),
        markdown: locale.value === 'fr' ? ParticipantsSettingsFr : ParticipantsSettingsEn,
      },
      {
        title: t('docs.participants.common_issues.title'),
        caption: t('docs.participants.common_issues.caption'),
        markdown: locale.value === 'fr' ? ParticipantsCommonIssuesFr : ParticipantsCommonIssuesEn,
      },
      {
        title: t('docs.participants.best_practices.title'),
        caption: t('docs.participants.best_practices.caption'),
        markdown: locale.value === 'fr' ? ParticipantsBestPracticesFr : ParticipantsBestPracticesEn,
      },
    ],
  },
])
</script>

<style scoped>
.bordered {
  border: 1px solid #ccc;
}
</style>
