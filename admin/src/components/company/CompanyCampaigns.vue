<template>
  <div>
    <q-btn
      v-if="isCompanyAdmin"
      size="sm"
      color="primary"
      :disable="campaignsStore.loading"
      :label="t('add')"
      icon="add"
      class="q-mb-md"
      @click="onAdd"
    />
    <div v-if="campaignsStore.loading">
      <q-spinner-dots color="primary" size="md" />
    </div>
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
      <q-separator />
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
import CompanyCampaign from 'src/components/company/CompanyCampaign.vue'
import CompanyCampaignDialog from 'src/components/company/CompanyCampaignDialog.vue'

const { t } = useI18n()
const authStore = useAuthStore()
const campaignsStore = useCampaigns()
const router = useRouter()

interface Props {
  company: Company
}
const props = defineProps<Props>()

const tab = ref<string | undefined>()
const showDialog = ref(false)
const selected = ref<Campaign>()
const campaigns = computed<Campaign[]>(() => campaignsStore.items || [])

const isCompanyAdmin = computed(() => {
  if (!props.company) return false
  return authStore.isAdmin || props.company.administrators?.includes(authStore.profile?.email || '')
})

onMounted(onInit)

watch(
  () => campaignsStore.items,
  () => {
    const ids = campaignsStore.items.map((item) => item.id + '')
    const queryCampaign = router.currentRoute.value.query.campaign as string | undefined
    if (queryCampaign && ids.includes(queryCampaign)) {
      tab.value = queryCampaign
      return
    }
    if (tab.value === undefined || (ids.length > 0 && !ids.includes(tab.value))) {
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
    open_workplaces: false,
  } as Campaign
  showDialog.value = true
}

function onSaved() {
  onInit()
}
</script>
