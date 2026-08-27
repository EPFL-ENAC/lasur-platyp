<template>
  <q-page class="q-pa-lg">
    <div class="title-bar">
      <div class="text-h6 row">
        <q-breadcrumbs gutter="sm" active-color="title">
          <q-breadcrumbs-el :label="t('companies')" to="/companies" />
          <q-breadcrumbs-el :label="company?.name" />
        </q-breadcrumbs>
      </div>
      <q-btn
        v-if="isCompanyAdmin"
        round
        size="sm"
        color="negative"
        icon="delete"
        :aria-label="t('remove')"
        class="q-ml-xs"
        @click="onShowRemove"
      />
    </div>

    <q-card flat class="q-my-lg">
      <q-card-section>
        <h5 class="text-h5 q-my-none">{{ t('overview') }}</h5>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <div class="row q-col-gutter-md q-mb-md">
          <div class="col-12 col-md-6">
            <fields-list :items="items" :dbobject="company" />
          </div>
          <div class="col-12 col-md-6">
            <fields-list :items="items2" :dbobject="company" />
          </div>
        </div>
      </q-card-section>

      <template v-if="isCompanyAdmin">
        <q-separator />

        <q-card-actions align="right">
          <q-btn size="sm" color="primary" icon="edit" :label="t('edit')" @click="onEdit" />
        </q-card-actions>
      </template>
    </q-card>

    <q-card flat class="q-my-xl">
      <q-card-section>
        <h5 class="text-h5 q-my-none">{{ t('company.actions') }}</h5>
      </q-card-section>

      <q-separator />

      <q-card-section>{{ t('company.employer_measures_description') }}</q-card-section>

      <template v-if="isCompanyAdmin">
        <q-separator />

        <q-card-actions align="right">
          <q-btn
            v-if="isCompanyAdmin"
            size="sm"
            color="primary"
            :label="t('company.custom_actions')"
            icon="settings"
            @click="onShowCustomActions"
          >
            <q-badge v-if="actionsStore.items.length" color="white" class="text-secondary q-ml-sm">
              {{ actionsStore.items.length }}
            </q-badge>
          </q-btn>
        </q-card-actions>
      </template>
    </q-card>

    <q-table
      v-if="company"
      class="q-my-xl"
      flat
      bordered
      :rows="campaigns"
      :columns="columns"
      table-header-class="bg-secondary-ultra-light text-secondary"
      row-key="id"
      :loading="campaignsStore.loading"
      :no-data-label="t('no_data')"
    >
      <template #top>
        <div class="title-bar">
          <h5 class="text-h5 q-my-none">{{ t('campaigns') }}</h5>

          <div class="title-toolbar">
            <q-btn
              v-if="isCompanyAdmin"
              size="md"
              color="primary"
              :disable="campaignsStore.loading"
              :label="t('add')"
              icon="add"
              @click="onAddCampaign"
            />
          </div>
        </div>
      </template>
      <!-- Custom Body Slot to handle the link -->
      <template #body-cell-name="props">
        <q-td :props="props">
          <router-link :to="`/company/${id}/campaign/${props.row.id}`" class="modus">
            {{ props.row.name }}
          </router-link>
        </q-td>
      </template>
      <template v-slot:body-cell-action="props">
        <q-td :props="props">
          <q-btn
            v-if="isCompanyAdmin"
            color="foreground"
            size="12px"
            flat
            dense
            round
            icon="visibility"
            :aria-label="t('view')"
            :to="`/company/${id}/campaign/${props.row.id}`"
          />
          <q-btn
            v-if="isCompanyAdmin"
            color="foreground"
            size="12px"
            flat
            dense
            round
            icon="edit"
            :aria-label="t('edit')"
            @click="onEditCampaign(props.row)"
          />
        </q-td>
      </template>
    </q-table>

    <company-dialog v-model="showDialog" :item="company" @saved="onSaved" />
    <confirm-dialog
      v-if="company"
      v-model="showRemoveDialog"
      :title="t('remove_company')"
      :text="t('remove_company_text', { name: company.name })"
      @confirm="onRemove"
    />
    <custom-actions-dialog
      v-if="company"
      v-model="showCustomActionsDialog"
      :company="company"
      @saved="onCustomActionsUpdated"
    />
    <company-campaign-dialog
      v-if="company && selectedCampaign"
      v-model="showCampaignDialog"
      :item="selectedCampaign"
      :company="company"
      @saved="onCampaignSaved"
    />
  </q-page>
</template>

<script setup lang="ts">
import type { Campaign, Company } from '@/models'
import type { Service } from '@/stores/services'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import CustomActionsDialog from '@/components/company/CustomActionsDialog.vue'
import type { FieldItem } from '@/components/FieldsList.vue'
import FieldsList from '@/components/FieldsList.vue'
import CompanyDialog from '@/components/company/CompanyDialog.vue'
import CompanyCampaignDialog from '@/components/company/CompanyCampaignDialog.vue'
import { notifySuccess, notifyError } from '@/utils/notify'
import type { QTableColumn } from 'quasar'
import { checkUrlParamNumber } from '@/utils/numbers'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()
const services = useServices()
const service = services.make('company') as Service<Company>
const actionsStore = useActions()
const campaignsStore = useCampaigns()

const id = computed(() => checkUrlParamNumber(route.params.id))
const company = ref<Company>()
const showRemoveDialog = ref(false)
const showDialog = ref(false)
const showCustomActionsDialog = ref(false)
const selectedCampaign = ref<Campaign>()
const showCampaignDialog = ref(false)

const isCompanyAdmin = computed(() => {
  if (!company.value) return false
  return authStore.isAdminOfThisCompany(company.value)
})

const items: FieldItem[] = [
  {
    field: 'name',
  },
  {
    field: 'administrators',
    label: 'company.administrators',
    format: (company: Company) => company.administrators?.join(', '),
  },
  {
    field: 'mobility_advisors',
    label: 'company.mobility_advisors',
    format: (company: Company) => company.mobility_advisors?.join(', '),
  },
]

const items2: FieldItem[] = [
  {
    field: 'contact_name',
    label: 'company.contact_name',
  },
  {
    field: 'contact_email',
    label: 'company.contact_email',
  },
  {
    field: 'info_url',
    label: 'company.info_url',
    links: (val) =>
      val.info_url
        ? [
            {
              label: val.info_url,
              to: val.info_url,
              iconRight: 'open_in_new',
            },
          ]
        : [],
  },
]

const campaigns = computed<Campaign[]>(() => campaignsStore.items || [])

const columns = computed<QTableColumn[]>(() => {
  const cols: QTableColumn[] = [
    {
      name: 'name',
      label: t('name'),
      field: 'name',
      align: 'left',
      sortable: true,
    },
    {
      name: 'start_date',
      label: t('start_date'), // Ensure this key exists in your i18n files
      field: 'start_date',
      align: 'right',
      sortable: true,
      // Optional: Format the date if needed
      format: (val: string) => (val ? new Date(val).toLocaleDateString() : '-'),
    },
    {
      name: 'end_date',
      label: t('end_date'),
      field: 'end_date',
      align: 'right',
      sortable: true,
      format: (val: string) => (val ? new Date(val).toLocaleDateString() : '-'),
    },
    {
      name: 'nb_employees',
      label: t('campaign.nb_employees'),
      field: 'nb_employees',
      align: 'right',
      sortable: true,
      format: (val: number) => `${val || 0}`,
    },
    {
      name: 'workplaces_count',
      label: t('campaign.workplaces.number'),
      field: (row: Campaign) => `${row.workplaces?.length || 0}`,
      align: 'right',
      sortable: true,
    },
  ]

  if (isCompanyAdmin.value) {
    cols.push({
      name: 'action',
      label: '',
      field: 'action',
      align: 'center',
    })
  }

  return cols
})

onMounted(() => {
  if (id.value === null) return
  onInit()
})

function onInit() {
  if (!id.value) return

  return Promise.all([
    service
      .get(id.value + '')
      .then((data: Company) => {
        company.value = data
        actionsStore.company = data
        actionsStore.load()
      })
      .catch(() => {
        notifyError(t('error.loading_company'))
        router.push('/companies')
      }),
    campaignsStore.loadIfNeeded(id.value).catch(notifyError),
  ])
}

function onEdit() {
  showDialog.value = true
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

function onSaved() {
  onInit()
}

function onShowCustomActions() {
  showCustomActionsDialog.value = true
}

function onCustomActionsUpdated() {
  actionsStore.load()
}

function onAddCampaign() {
  selectedCampaign.value = {
    name: '',
    company_id: company.value?.id || 0,
    open_workplaces: false,
    with_professional_questions: true,
  } as Campaign
  showCampaignDialog.value = true
}

function onEditCampaign(campaign: Campaign) {
  selectedCampaign.value = campaign
  showCampaignDialog.value = true
}

function onCampaignSaved() {
  campaignsStore.load().catch(notifyError)
}
</script>
