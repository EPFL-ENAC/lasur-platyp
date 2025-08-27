<template>
  <q-card v-if="withInfo" class="bg-primary">
    <q-card-section>
      <q-markdown :src="info" class="q-mt-md text-bold" />
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
const { t } = useI18n()
const collector = useCollector()

const withInfo = computed(
  () => collector.info.contact_name || collector.info.contact_email || collector.info.info_url,
)

const info = computed(() => {
  if (!collector.info) return ''

  const hasContact = collector.info.contact_name || collector.info.contact_email

  return `
${
  hasContact
    ? t('contact.description', {
        company_name: collector.info.company_name,
        contact_name: collector.info.contact_name,
        contact_email: collector.info.contact_email,
      })
    : ''
}

${
  collector.info.info_url
    ? t('contact.website', {
        info_url: collector.info.info_url,
      })
    : ''
}
`
})
</script>
