<template>
  <q-page>
    <div class="title-bar q-pa-md">
      <div class="text-h4 row">
        <q-breadcrumbs gutter="sm" active-color="title">
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
          :aria-label="t('remove')"
          @click="onShowRemove"
          style="width: 32px"
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
import { checkUrlParamNumber } from 'src/utils/numbers'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()
const services = useServices()
const companyService = services.make('company') as Service<Company>
const campaignService = services.make('campaign') as Service<Campaign>
const actionsStore = useActions()
const campaignsStore = useCampaigns()

const companyId = computed(() => checkUrlParamNumber(route.params.companyId))
const campaignId = computed(() => checkUrlParamNumber(route.params.campaignId))
const company = ref<Company>()
const showRemoveDialog = ref(false)
const showCampaignDialog = ref(false)

const isCompanyAdmin = computed(() => {
  if (!company.value) return false
  return authStore.isAdminOfThisCompany(company.value)
})

const campaign = computed<Campaign | undefined>(() =>
  campaignsStore.items?.find((c) => c.id === campaignId.value),
)

onMounted(() => {
  if (companyId.value === undefined) return
  onInit()
})

function onInit() {
  if (!companyId.value) return
  
  return Promise.all([
    companyService
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
  if (!campaign.value || !company.value) return
  campaignService.remove(campaign.value.id + '').then(() => {
    notifySuccess(t('campaign_removed'))
    router.push(`/company/${company.value!.id}`)
  }).catch(notifyError)
}

function onCampaignSaved() {
  loadCampaigns()
}
</script>
