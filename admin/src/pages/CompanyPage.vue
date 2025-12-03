<template>
  <q-page>
    <div class="text-h5 q-pa-md row">
      <q-breadcrumbs gutter="sm">
        <q-breadcrumbs-el :label="t('companies')" to="/companies" />
        <q-breadcrumbs-el :label="company?.name" />
      </q-breadcrumbs>
      <q-btn
        v-if="authStore.isAdmin"
        flat
        dense
        size="sm"
        color="primary"
        icon="edit"
        class="on-right"
        @click="onEdit"
      />
      <q-btn
        v-if="authStore.isAdmin"
        flat
        dense
        size="sm"
        color="negative"
        icon="delete"
        class="q-ml-xs"
        @click="onShowRemove"
      />
      <q-btn
        :label="t('report')"
        outline
        size="sm"
        color="info"
        icon="bar_chart"
        class="on-right"
        @click="onShowStats"
      />
    </div>
    <q-separator />
    <div class="q-pa-md">
      <div class="row q-col-gutter-md q-mb-md">
        <div class="col-12 col-md-6">
          <fields-list :items="items" :dbobject="company" />
        </div>
        <div class="col-12 col-md-6">
          <fields-list :items="items2" :dbobject="company" />
        </div>
      </div>
      <div class="q-mb-sm">{{ t('company.actions') }}</div>
      <q-btn
        v-if="authStore.isAdmin"
        size="sm"
        color="primary"
        :label="t('company.custom_actions')"
        icon="settings"
        class="q-mb-md"
        @click="onShowCustomActions"
      >
        <q-badge v-if="actionsStore.items.length" color="white" class="text-secondary q-ml-sm">{{
          actionsStore.items.length
        }}</q-badge>
      </q-btn>
      <div v-if="company?.actions">
        <div class="row q-col-gutter-md q-mb-md">
          <div class="col-12 col-md-6">
            <div class="text-hint q-mb-sm">{{ t('actions.personnal') }}</div>
            <fields-list :items="actionItems" :dbobject="formattedActions" />
          </div>
          <div class="col-12 col-md-6">
            <div class="text-hint q-mb-sm">{{ t('actions.professional') }}</div>
            <fields-list :items="actionProItems" :dbobject="formattedActions" />
          </div>
        </div>
      </div>
      <div class="text-h6 q-mb-sm">{{ t('campaigns') }}</div>
      <company-campaigns v-if="company" :company="company" />
    </div>
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
    <company-charts-dialog v-if="company" v-model="showChartsDialog" :company="company" />
  </q-page>
</template>

<script setup lang="ts">
import type { Company, EmployerActions } from 'src/models'
import type { Service } from 'src/stores/services'
import CompanyCampaigns from 'src/components/company/CompanyCampaigns.vue'
import ConfirmDialog from 'src/components/ConfirmDialog.vue'
import CustomActionsDialog from 'src/components/company/CustomActionsDialog.vue'
import type { FieldItem } from 'src/components/FieldsList.vue'
import FieldsList from 'src/components/FieldsList.vue'
import CompanyDialog from 'src/components/company/CompanyDialog.vue'
import CompanyChartsDialog from 'src/components/company/CompanyChartsDialog.vue'
import { notifySuccess } from 'src/utils/notify'
import { actionItems, actionProItems } from 'src/utils/options'

const route = useRoute()
const router = useRouter()
const { t, locale } = useI18n()
const authStore = useAuthStore()
const services = useServices()
const service = services.make('company') as Service<Company>
const actionsStore = useActions()

const id = computed(() => route.params.id)
const company = ref<Company>()
const showRemoveDialog = ref(false)
const showDialog = ref(false)
const showCustomActionsDialog = ref(false)
const showChartsDialog = ref(false)

const formattedActions = computed(() => {
  const allActions: EmployerActions = {}
  if (company.value?.actions) {
    Object.keys(company.value.actions).forEach((group) => {
      allActions[group] =
        company.value?.actions && company.value.actions[group]
          ? company.value.actions[group].map((action) => {
              // check action can be parsed as a number
              const actionId = parseInt(action, 10)
              if (!isNaN(actionId)) {
                const labels = actionsStore.items.find((a) => a.id === actionId)?.labels
                if (labels) {
                  return labels[locale.value] || labels.en || action
                }
                return action
              }
              return t(`actions.${action}`)
            })
          : []
    })
  }
  return allActions
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

onMounted(() => {
  if (id.value === undefined) return
  onInit()
})

function onInit() {
  service.get(id.value + '').then((data: Company) => {
    company.value = data
    actionsStore.company = data
    actionsStore.load()
  })
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

function onShowStats() {
  showChartsDialog.value = true
}
</script>
