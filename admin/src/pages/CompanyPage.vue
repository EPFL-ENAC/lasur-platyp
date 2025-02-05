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
    </div>
    <q-separator />
    <div class="q-pa-md">
      <div class="row q-col-gutter-md q-mb-md">
        <div class="col-12 col-md-6">
          <fields-list :items="items" :dbobject="company" />
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
  </q-page>
</template>

<script setup lang="ts">
import type { Company } from 'src/models'
import type { Service } from 'src/stores/services'
import CompanyCampaigns from 'src/components/CompanyCampaigns.vue'
import ConfirmDialog from 'src/components/ConfirmDialog.vue'
import type { FieldItem } from 'src/components/FieldsList.vue'
import FieldsList from 'src/components/FieldsList.vue'
import CompanyDialog from 'src/components/CompanyDialog.vue'
import { notifySuccess } from 'src/utils/notify'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()
const services = useServices()
const service = services.make('company') as Service<Company>

const id = computed(() => route.params.id)
const company = ref<Company>()
const showRemoveDialog = ref(false)
const showDialog = ref(false)

const items: FieldItem[] = [
  {
    field: 'name',
  },
  {
    field: 'administrators',
    label: t('company.administrators'),
    format: (company: Company) => company.administrators?.join(', '),
  },
]

onMounted(() => {
  if (id.value === undefined) return
  onInit()
})

function onInit() {
  service.get(id.value + '').then((data: Company) => {
    company.value = data
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
</script>
