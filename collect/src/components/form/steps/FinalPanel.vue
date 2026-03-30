<template>
  <div>
    <div class="text-h4 text-center q-mb-xl">
      {{ t('form.final') }}
    </div>
    <div v-if="collector.info.rewards_message" class="q-mb-xl">
      <div class="text-h5 text-center q-mb-md">
        {{ t('form.final_rewards.title') }}
      </div>
      <p>{{ collector.info.rewards_message?.[locale] }}</p>

      <div class="row justify-center q-mt-lg">
        <q-btn
          rounded
          color="accent"
          :label="t('form.final_rewards.download')"
          icon-right="download"
          size="lg"
          @click="downloadPdf()"
        />
      </div>
    </div>
    <InfoPanel />
  </div>
</template>

<script setup lang="ts">
import InfoPanel from 'src/components/form/steps/InfoPanel.vue'

const { t, locale } = useI18n()
const survey = useSurvey()
const collector = useCollector()

onMounted(() => {
  survey.finish()
})

async function downloadPdf() {
  const { jsPDF } = await import('jspdf')
  const doc = new jsPDF()

  const pageWidth = doc.internal.pageSize.getWidth()
  const margin = 10
  const maxWidth = pageWidth - margin * 2

  const rewardMessage = collector.info.rewards_message?.[locale.value] || ''
  const wrappedMessage = doc.splitTextToSize(rewardMessage, maxWidth)

  let y = 10

  doc.text(wrappedMessage, margin, y)
  y += wrappedMessage.length * 7

  y += 20

  if (collector.responseId) {
    const participationText = t('form.final_rewards.participation_id', {
      id: collector.responseId,
    })
    const wrappedParticipation = doc.splitTextToSize(participationText, maxWidth)

    doc.text(wrappedParticipation, margin, y)
  }

  doc.save('attestation.pdf')
}
</script>
