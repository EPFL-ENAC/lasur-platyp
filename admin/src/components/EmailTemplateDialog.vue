<template>
  <q-dialog v-model="open">
    <q-card class="dialog-lg">
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">
          {{
            t('campaign.email_template.modalTitle', {
              campaign: props.campaign.name,
            })
          }}
        </div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>

      <q-separator q-mt-md />

      <q-card-section>
        <div class="row q-col-gutter-md">
          <q-input
            v-model="surveyLink"
            outlined
            rounded
            color="field"
            class="col-12"
            :label="t('campaign.email_template.surveyLink')"
            readonly
          />
          <q-input
            v-model="contactEmail"
            outlined
            rounded
            color="field"
            class="col-12 col-sm-6"
            :label="t('campaign.email_template.contactEmail')"
          />
          <q-input
            v-model="contactName"
            outlined
            rounded
            color="field"
            class="col-12 col-sm-6"
            :label="t('campaign.email_template.contactName')"
          />
        </div>
      </q-card-section>

      <q-tabs
        v-model="tab"
        dense
        active-color="secondary"
        active-bg-color="background"
        active-class="tab-active"
        indicator-color="transparent"
        class="bg-secondary-ultra-light q-mx-md"
        align="justify"
        narrow-indicator
      >
        <q-tab name="fr" label="Français" />
        <q-tab name="en" label="English" />
      </q-tabs>

      <q-tab-panels v-model="tab" animated>
        <q-tab-panel v-for="lang in ['fr', 'en']" :key="lang" :name="lang">
          <div :id="`email-content-${lang}`" class="q-pa-md bg-background rounded-borders">
            <q-markdown
              :src="
                t(
                  'campaign.email_template.template',
                  {
                    surveyLink: surveyLink,
                    contactEmail: contactEmail || t('campaign.email_template.defaultContactEmail'),
                    contactName: contactName || t('campaign.email_template.defaultContactName'),
                  },
                  { locale: lang },
                )
              "
              no-heading-anchor-links
            />
          </div>
        </q-tab-panel>
      </q-tab-panels>

      <q-separator />

      <q-card-actions align="right">
        <q-btn
          color="primary"
          icon="content_copy"
          :label="t('campaign.email_template.copyTemplate')"
          @click="copyAsRichText"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import type { Campaign } from '@/models'
import { makeSurveyLink } from '@/utils/links'
import { notifyError, notifySuccess } from '@/utils/notify'

const { t, locale } = useI18n()

const open = defineModel<boolean>({
  default: false,
})

interface DialogProps {
  campaign: Campaign
}

const props = defineProps<DialogProps>()

const tab = ref(locale.value.includes('fr') ? 'fr' : 'en')
const contactEmail = ref(props.campaign.contact_email || '')
const contactName = ref(props.campaign.contact_name || '')

const surveyLink = computed(() => {
  if (!props.campaign.slug) return ''
  return makeSurveyLink(props.campaign.slug)
})

async function copyAsRichText() {
  const el = document.getElementById(`email-content-${tab.value}`)
  if (!el) return

  try {
    const clipboard = navigator.clipboard
    // Try rich-text copy when supported
    if (
      typeof ClipboardItem !== 'undefined' &&
      clipboard &&
      typeof clipboard.write === 'function'
    ) {
      const htmlBlob = new Blob([el.innerHTML], { type: 'text/html' })
      const textBlob = new Blob([el.innerText], { type: 'text/plain' })
      const data = [
        new ClipboardItem({
          'text/html': htmlBlob,
          'text/plain': textBlob,
        }),
      ]
      await clipboard.write(data)
    } else if (clipboard && typeof clipboard.writeText === 'function') {
      // Fallback: copy plain text only
      await clipboard.writeText(el.innerText)
    } else {
      throw new Error('Clipboard API not supported in this browser/context')
    }

    notifySuccess(t('campaign.email_template.copyTemplateSuccess'))
  } catch (err) {
    console.error('Failed to copy: ', err)
    notifyError(t('campaign.email_template.copyTemplateError'))
  }
}
</script>
