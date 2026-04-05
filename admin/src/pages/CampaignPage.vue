<template>
  <q-page>
    <div class="title-bar q-pa-md">
      <div class="text-h4 row">
        <q-breadcrumbs gutter="sm" active-color="primary-dark">
          <q-breadcrumbs-el :label="t('companies')" to="/companies" />
          <q-breadcrumbs-el :label="company?.name" :to="`/company/${company?.id}`" />
          <q-breadcrumbs-el :label="campaign?.name" />
        </q-breadcrumbs>
      </div>

      <div class="title-toolbar">
        <q-btn
          v-if="isCompanyAdmin"
          size="sm"
          color="primary"
          icon="edit"
          :label="t('edit')"
          @click="onEdit"
        />
        <q-btn
          v-if="isCompanyAdmin"
          round
          size="sm"
          color="negative"
          icon="delete"
          @click="onShowRemove"
          style="width: 32px;"
        />
      </div>
    </div>

    <company-campaign v-if="campaign && company" :item="campaign" :company="company" />

    <confirm-dialog
      v-if="campaign"
      v-model="showRemoveDialog"
      :title="t('remove_campaign')"
      :text="t('remove_campaign_text', { name: campaign.name })"
      @confirm="onRemove"
    />    
    <company-campaign-dialog
      v-if="company && campaign"
      v-model="showCampaignDialog"
      :item="campaign"
      :company="company"
      @saved="onCampaignSaved"
    />
  </q-page>
</template>

<script setup lang="ts">
import type { Campaign, Company } from 'src/models'
import type { Service } from 'src/stores/services'
import ConfirmDialog from 'src/components/ConfirmDialog.vue'
import CompanyCampaign from 'src/components/company/CompanyCampaign.vue'
import CompanyCampaignDialog from 'src/components/company/CompanyCampaignDialog.vue'
import { notifySuccess, notifyError } from 'src/utils/notify'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()
const services = useServices()
const service = services.make('company') as Service<Company>
const actionsStore = useActions()
const campaignsStore = useCampaigns()

const companyId = computed(() => route.params.companyId === undefined ? undefined : Number(route.params.companyId))
const campaignId = computed(() => route.params.campaignId === undefined ? undefined : Number(route.params.campaignId))
const company = ref<Company>()
const showRemoveDialog = ref(false)
const showCampaignDialog = ref(false)

const isCompanyAdmin = computed(() => {
  if (!company.value) return false
  return authStore.isAdmin || company.value.administrators?.includes(authStore.profile?.email || '')
})

const campaign = computed<Campaign | undefined>(() => campaignsStore.items?.find((c) => c.id === campaignId.value))

onMounted(() => {
  if (companyId.value === undefined) return
  onInit()
})

function onInit() {
  return Promise.all([
    service
      .get(companyId.value + '')
      .then((data: Company) => {
        company.value = data
        actionsStore.company = data
        actionsStore.load()
      })
      .catch(() => {
        notifyError(t('error.loading_company'))
        router.push('/companies')
      }),
    campaignsStore.loadIfNeeded(companyId.value).catch(notifyError),
  ])
}

function loadCampaigns() {
  return campaignsStore.load().catch(notifyError)
}

function onEdit() {
  showCampaignDialog.value = true
}

function onShowRemove() {
  showRemoveDialog.value = true
}

function onRemove() {
  if (!company.value) return
  service.remove(company.value.id + '').then(() => {
    notifySuccess(t('company_removed'))
    router.push('/companies')
  })
}

function onCampaignSaved() {
  loadCampaigns()
}
</script>
