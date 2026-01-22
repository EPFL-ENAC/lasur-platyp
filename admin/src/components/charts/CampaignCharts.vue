<template>
  <div>
    <q-spinner-dots v-if="loading" size="md" />
    <div class="row" v-if="!loading && hasRecords">
      <div class="col-12 col-md-4">
        <campaign-counts-chart v-if="campaignStats" :stats="campaignStats" :height="300" />
      </div>
      <div class="col-12 col-md-8">
        <campaign-history-chart v-if="campaignStats" :stats="campaignStats" :height="300" />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import type { Campaign, CampaignStats } from 'src/models'
import CampaignCountsChart from './CampaignCountsChart.vue'
import CampaignHistoryChart from './CampaignHistoryChart.vue'

interface Props {
  item: Campaign
}
const props = defineProps<Props>()

const stats = useStats()

const loading = ref(false)
const campaignStats = ref<CampaignStats>()

const hasRecords = computed(() => {
  return campaignStats.value?.total_records && campaignStats.value.total_records > 0
})

onMounted(() => {
  if (props.item.id) {
    loading.value = true
    stats
      .getCampaignStats(props.item.id)
      .then((data) => {
        campaignStats.value =
          data ||
          ({
            name: props.item.name,
            company_id: props.item.company_id,
            campaign_id: props.item.id,
            nb_employees: props.item.nb_employees || 0,
            completed_records: 0,
            total_records: 0,
            weekly: [],
          } as CampaignStats)
      })
      .finally(() => {
        loading.value = false
      })
  }
})
</script>
