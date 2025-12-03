<template>
  <q-dialog v-model="showDialog" persistent @hide="onHide" style="min-height: 500px">
    <q-card class="dialog-md">
      <q-card-section>
        <q-toolbar>
          <q-toolbar-title>
            <span>{{ company?.name }}</span>
            <span v-if="campaign"> - {{ campaign?.name }}</span>
          </q-toolbar-title>
          <q-btn flat icon="close" v-close-popup />
        </q-toolbar>
      </q-card-section>
      <q-separator />
      <q-card-section>
        <charts-carousel v-if="!stats.loading" :percent="true" :height="500" />
        <div v-else class="row justify-center">
          <q-spinner-dots color="primary" size="50px" />
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>
<script setup lang="ts">
import ChartsCarousel from 'src/components/charts/ChartsCarousel.vue'
import type { Campaign, Company } from 'src/models'
import type { Filter } from 'src/components/models'

interface DialogProps {
  modelValue: boolean
  company: Company
  campaign?: Campaign
}

const props = defineProps<DialogProps>()
const emit = defineEmits(['update:modelValue'])

const stats = useStats()
const showDialog = ref(props.modelValue)

watch(
  () => props.modelValue,
  (value) => {
    showDialog.value = value
    if (!value) {
      return
    }
    const query = {
      company_id: { $eq: props.company.id },
    } as Filter
    if (props.campaign) {
      query.campaign_id = { $eq: props.campaign.id }
    }
    stats.loadStats(query).catch(() => {})
  },
)

function onHide() {
  showDialog.value = false
  emit('update:modelValue', false)
}
</script>
