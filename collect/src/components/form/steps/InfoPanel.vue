<template>
  <q-card flat v-if="withInfo">
    <q-card-section>
      <div class="row items-start">
        <q-icon
          name="info"
          color="primary"
          size="sm"
          class="q-mr-md q-mt-xs"
        />
        <div>
          <div class="text-h6">
            {{ t('contact.header', { company_name: collector.info.company_name }) }}
          </div>
          <div v-if="hasContact">
            {{
              t('contact.contact_line', {
                contact_name: collector.info.contact_name,
                contact_email: collector.info.contact_email,
              })
            }}
          </div>
          <div class="row q-mt-sm q-gutter-sm">
            <q-btn
              v-if="collector.info.contact_email"
              flat
              dense
              no-caps
              color="primary"
              icon="content_copy"
              :label="t('contact.copy_email')"
              @click="copyEmail"
            />
            <q-btn
              v-if="collector.info.info_url"
              flat
              dense
              no-caps
              color="primary"
              icon="open_in_new"
              :label="t('contact.more_info')"
              :href="collector.info.info_url"
              target="_blank"
              rel="noopener noreferrer"
            />
          </div>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { Notify } from 'quasar'
const { t } = useI18n()
const collector = useCollector()

const withInfo = computed(
  () => collector.info.contact_name || collector.info.contact_email || collector.info.info_url,
)

const hasContact = computed(
  () => collector.info.contact_name || collector.info.contact_email,
)

function copyEmail() {
  if (collector.info.contact_email) {
    void navigator.clipboard.writeText(collector.info.contact_email)
    Notify.create({
      type: 'positive',
      message: t('contact.copied'),
    })
  }
}
</script>