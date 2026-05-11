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
          v-if="rewardUrl"
          rounded
          color="accent"
          :label="t('form.final_rewards.download')"
          icon-right="download"
          size="lg"
          :href="rewardUrl"
          target="_blank"
          rel="noopener noreferrer"
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

const rewardUrl = computed(() => {
  if (!collector.token) return null

  return `/certificate/${collector.token}`
})

onMounted(() => {
  survey.finish()
})

</script>
