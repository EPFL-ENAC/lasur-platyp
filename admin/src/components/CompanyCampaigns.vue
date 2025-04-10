<template>
  <div>
    <q-btn
      v-if="authStore.isAdmin"
      size="sm"
      color="primary"
      :disable="campaignsStore.loading"
      :label="t('add')"
      icon="add"
      class="q-mb-md"
      @click="onAdd"
    />
    <div v-if="!campaignsStore.loading && campaigns.length > 0">
      <q-tabs
        v-model="tab"
        dense
        no-caps
        class="text-grey"
        active-color="secondary"
        active-bg-color="grey-4"
        indicator-color="primary"
        align="left"
      >
        <q-tab
          v-for="campaign in campaigns"
          :key="`${campaign.id}`"
          :name="`${campaign.id}`"
          :label="campaign.name"
        />
      </q-tabs>
      <q-tab-panels v-model="tab">
        <q-tab-panel
          v-for="campaign in campaigns"
          :key="`${campaign.id}`"
          :name="`${campaign.id}`"
          class="bg-grey-2"
        >
          <company-campaign :item="campaign" :company="company" />
        </q-tab-panel>
      </q-tab-panels>
    </div>
    <company-campaign-dialog
      v-if="company && selected"
      v-model="showDialog"
      :item="selected"
      :company="company"
      @saved="onSaved"
    />
  </div>
</template>

<script setup lang="ts">
import type { Campaign, Company } from 'src/models'
import { notifyError } from 'src/utils/notify'
import CompanyCampaign from 'src/components/CompanyCampaign.vue'
import CompanyCampaignDialog from 'src/components/CompanyCampaignDialog.vue'

const { t } = useI18n()
const authStore = useAuthStore()
const campaignsStore = useCampaigns()

interface Props {
  company: Company
}
const props = defineProps<Props>()

const tab = ref<string | undefined>()
const showDialog = ref(false)
const selected = ref<Campaign>()
const campaigns = computed<Campaign[]>(() => campaignsStore.items || [])

onMounted(onInit)

watch(
  () => campaignsStore.items,
  () => {
    const ids = campaignsStore.items.map((item) => item.id + '')
    if (tab.value === undefined || !ids.includes(tab.value)) {
      tab.value = campaigns.value.length ? campaigns.value[0]?.id + '' : ''
    }
  },
)

function onInit() {
  campaignsStore.company = props.company
  campaignsStore.load().catch(notifyError)
}

function onAdd() {
  selected.value = {
    name: '',
    company_id: props.company.id,
  } as Campaign
  showDialog.value = true
}

function onSaved() {
  onInit()
}
</script>
