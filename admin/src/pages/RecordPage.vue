<template>
  <q-page class="q-pa-lg">
    <div class="text-h6 row">
      <q-breadcrumbs gutter="sm" active-color="title">
        <q-breadcrumbs-el :label="t('records')" to="/records" />
        <q-breadcrumbs-el :label="record?.token" />
      </q-breadcrumbs>
    </div>
    <q-card flat class="q-my-lg">
      <q-card-section>
        <div class="text-h5 q-my-none">{{ t('record.raw_data') }}</div>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-6">
            <fields-list :items="items1" :dbobject="record" />
          </div>
          <div class="col-12 col-md-6">
            <fields-list :items="items2" :dbobject="record" />
          </div>
        </div>
        <q-list bordered class="q-mt-md">
          <q-expansion-item
            :label="t('record.data')"
            icon="data_object"
            expand-icon="expand_more"
            header-class="bg-super-muted text-foreground"
          >
            <div class="row q-col-gutter-md q-pa-md">
              <div class="col-12 col-md-6">
                <fields-list :items="dataItems1" :dbobject="record?.data" />
              </div>
              <div class="col-12 col-md-6">
                <fields-list :items="dataItems2" :dbobject="record?.data" />
              </div>
            </div>
          </q-expansion-item>
        </q-list>

        <q-list bordered class="q-mt-md">
          <q-expansion-item
            :label="t('record.typo')"
            icon="commute"
            expand-icon="expand_more"
            header-class="bg-super-muted text-foreground"
          >
            <div class="row q-col-gutter-md q-pa-md">
              <div class="col-12 col-md-6">
                <div class="text-bold q-mb-sm">{{ t('record.typo_reco') }}</div>
                <fields-list :items="typoRecoItems" :dbobject="record?.typo?.reco" />
                <div class="text-bold q-mb-sm q-mt-lg">{{ t('record.typo_reco_actions') }}</div>
                <fields-list :items="typoRecoActionsItems" :dbobject="record?.typo?.reco_actions" />
              </div>
              <div class="col-12 col-md-6">
                <div class="text-bold q-mb-sm">{{ t('record.typo_reco_pro') }}</div>
                <fields-list :items="typoRecoProItems" :dbobject="record?.typo?.reco_pro" />
                <div class="text-bold q-mb-sm q-mt-lg">
                  {{ t('record.typo_reco_pro_actions') }}
                </div>
                <fields-list
                  :items="typoRecoProActionsItems"
                  :dbobject="record?.typo?.reco_actions"
                />
              </div>
            </div>
          </q-expansion-item>
        </q-list>
      </q-card-section>
    </q-card>
    <q-card flat class="q-my-xl">
      <q-card-section>
        <div class="text-h5">{{ t('record.isochrones') }}</div>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <div class="text-help q-mb-md">{{ t('record.isochrones_hint') }}</div>
        <div class="text-help q-mb-md">
          {{ t('record.reco', { mode: reco }) }}
        </div>
        <IsochronesMap
          v-if="record && reco && origin"
          :mapId="`map-record-${record.id}`"
          :center="origin"
          :reco="reco"
          :height="'600px'"
          :zoom="11"
        />
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import type { Company, Campaign } from '@/models'
import IsochronesMap from '@/components/IsochronesMap.vue'
import FieldsList from '@/components/FieldsList.vue'
import type { FieldItem } from '@/components/FieldsList.vue'
import type { Record } from '@/models'
import { notifyError } from '@/utils/notify'

interface Location {
  lat: number
  lon: number
}

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const services = useServices()
const recordService = services.make('record') as Service<Record>
const companyService = services.make('company') as Service<Company>
const campaignService = services.make('campaign') as Service<Campaign>

const id = computed(() => route.params.id)
const record = ref<Record>()
const company = ref<Company>()
const campaign = ref<Campaign>()

const origin = computed(() => {
  if (record.value?.data?.origin) {
    const orig = record.value.data.origin as unknown as Location
    return [orig.lon, orig.lat] as [number, number]
  }
  return undefined
})

const reco = computed(() => {
  const recommendations =
    (record.value?.typo?.reco?.reco_dt2 as string[]) ||
    (record.value?.typo?.reco?.reco_inter as string[]) ||
    []
  return recommendations.length > 0 ? recommendations[0] : undefined
})

onMounted(() => {
  if (id.value === undefined) return
  onInit()
})

const items = computed<FieldItem[]>(() => {
  return [
    { field: 'token', label: 'token' },
    {
      field: 'company_id',
      label: 'company.label',
      links: (val) => [
        {
          label: company.value?.name || val.company_id,
          to: `/company/${val.company_id}`,
          icon: 'business',
        },
        {
          label: campaign.value?.name || val.campaign_id,
          to: `/company/${val.company_id}/campaign/${val.campaign_id}`,
          icon: 'campaign',
        },
      ],
    },
    {
      field: 'created_at',
      format: (val) => new Date(val.created_at).toLocaleString(),
    },
    {
      field: 'updated_at',
      format: (val) => new Date(val.updated_at).toLocaleString(),
    },
    { field: 'comments', label: 'comments' },
  ]
})
const items1 = computed<FieldItem[]>(() => {
  // First half of items
  return items.value.slice(0, Math.ceil(items.value.length / 2))
})
const items2 = computed<FieldItem[]>(() => {
  // Second half of items
  return items.value.slice(Math.ceil(items.value.length / 2))
})

const dataItems = computed<FieldItem[]>(() => {
  return record.value?.data ? Object.keys(record.value.data).map((key) => ({ field: key })) : []
})
const dataItems1 = computed<FieldItem[]>(() => {
  // First half of data items
  const allItems = dataItems.value
  return allItems.slice(0, Math.ceil(allItems.length / 2))
})
const dataItems2 = computed<FieldItem[]>(() => {
  // Second half of data items
  const allItems = dataItems.value
  return allItems.slice(Math.ceil(allItems.length / 2))
})

const typoRecoItems = computed<FieldItem[]>(() => {
  return record.value?.typo?.reco
    ? Object.keys(record.value.typo.reco)
        .filter((key) => !['access', 'scores'].includes(key))
        .map((key) => ({ field: key }))
    : []
})
const typoRecoActionsItems = computed<FieldItem[]>(() => {
  return record.value?.typo?.reco_actions
    ? Object.keys(record.value.typo.reco_actions)
        .filter((key) => !key.includes('_pro'))
        .map((key) => ({ field: key }))
    : []
})
const typoRecoProItems = computed<FieldItem[]>(() => {
  return record.value?.typo?.reco_pro
    ? Object.keys(record.value.typo.reco_pro).map((key) => ({ field: key }))
    : []
})
const typoRecoProActionsItems = computed<FieldItem[]>(() => {
  return record.value?.typo?.reco_actions
    ? Object.keys(record.value.typo.reco_actions)
        .filter((key) => key.includes('_pro'))
        .map((key) => ({ field: key }))
    : []
})
function onInit() {
  recordService
    .get(id.value + '')
    .then((data: Record) => {
      record.value = data
      if (data.company_id) {
        companyService
          .get(data.company_id + '')
          .then((compData: Company) => {
            company.value = compData
          })
          .catch(() => {
            console.warn('Could not load company for record display: ', data.company_id)
          })
      }
      if (data.campaign_id) {
        campaignService
          .get(data.campaign_id + '')
          .then((campData: Campaign) => {
            campaign.value = campData
          })
          .catch(() => {
            console.warn('Could not load campaign for record display: ', data.campaign_id)
          })
      }
    })
    .catch(() => {
      notifyError(t('error.loading_record'))
      router.push('/records')
    })
}
</script>
