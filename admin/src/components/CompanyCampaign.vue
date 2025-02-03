<template>
  <div>
    <q-btn
      v-if="authStore.isAdmin"
      size="sm"
      color="primary"
      icon="edit"
      class="q-mb-md"
      @click="onEdit"
    />
    <pre>{{ props.item }}</pre>
    <div class="text-h6 q-mb-sm">{{ t('participants') }}</div>
    <company-campaign-dialog
      v-if="props.company"
      v-model="showDialog"
      :item="props.item"
      :company="props.company"
      @saved="onSaved"
    />
  </div>
</template>

<script setup lang="ts">
import type { Campaign, Company } from 'src/models'
import CompanyCampaignDialog from 'src/components/CompanyCampaignDialog.vue'

const { t } = useI18n()
const authStore = useAuthStore()
const campaignsStore = useCampaigns()

interface Props {
  item: Campaign
  company: Company
}
const props = defineProps<Props>()

const showDialog = ref(false)

function onEdit() {
  showDialog.value = true
}

function onSaved() {
  campaignsStore.load()
}
</script>
