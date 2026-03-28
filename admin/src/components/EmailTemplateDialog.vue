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
            class="col-12"
            :label="t('campaign.email_template.surveyLink')"
            readonly
            filled
          />
          <q-input
            v-model="contactEmail"
            class="col-12 col-sm-6"
            :label="t('campaign.email_template.contactEmail')"
            outlined
          />
          <q-input
            v-model="contactName"
            class="col-12 col-sm-6"
            :label="t('campaign.email_template.contactName')"
            outlined
          />
        </div>
      </q-card-section>

      <q-tabs
        v-model="tab"
        dense
        class="text-grey"
        active-color="primary"
        indicator-color="primary"
        align="justify"
        narrow-indicator
      >
        <q-tab name="fr" label="Français" />
        <q-tab name="en" label="English" />
      </q-tabs>

      <q-separator />

      <q-tab-panels v-model="tab" animated>
        <q-tab-panel v-for="lang in ['fr', 'en']" :key="lang" :name="lang">
          <div :id="`email-content-${lang}`" class="q-pa-md bg-grey-1 rounded-borders">
            <q-markdown
              :src="
                t('campaign.email_template.template', {
                  surveyLink: surveyLink,
                  contactEmail:
                    contactEmail || t('campaign.email_template.defaultContactEmail'),
                  contactName:
                    contactName || t('campaign.email_template.defaultContactName'),
                }, { locale: lang })
              "
              no-heading-anchor-links
            />
          </div>
      </q-tab-panel>
      </q-tab-panels>
      
      <q-separator />
    
      <q-card-actions align="right" class="bg-grey-3">
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
import type { Campaign } from 'src/models';
import { makeSurveyLink } from 'src/utils/links';
import { notifyError, notifySuccess } from 'src/utils/notify';

const { t, locale } = useI18n();

const open = defineModel<boolean>({
  default: false,
});

interface DialogProps {
  campaign: Campaign;
}

const props = defineProps<DialogProps>();

const tab = ref(locale.value.includes('fr') ? 'fr' : 'en');
const contactEmail = ref(props.campaign.contact_email || '');
const contactName = ref(props.campaign.contact_name || '');

const surveyLink = computed(() => {
  if (!props.campaign.slug) return '';
  return makeSurveyLink(props.campaign.slug);
});

async function copyAsRichText() {
  const el = document.getElementById(`email-content-${tab.value}`);
  if (!el) return;

  try {
    // We create a blob of the HTML content
    const htmlBlob = new Blob([el.innerHTML], { type: 'text/html' });
    const textBlob = new Blob([el.innerText], { type: 'text/plain' });

    const data = [
      new ClipboardItem({
        'text/html': htmlBlob,
        'text/plain': textBlob,
      }),
    ];

    await navigator.clipboard.write(data);

    notifySuccess(t('campaign.email_template.copyTemplateSuccess'));
  } catch (err) {
    console.error('Failed to copy: ', err);
    notifyError(t('campaign.email_template.copyTemplateError'));
  }
}
</script>