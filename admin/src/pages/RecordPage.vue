<template>
  <q-page>
    <div class="text-h5 q-pa-md row">
      <q-breadcrumbs gutter="sm">
        <q-breadcrumbs-el :label="t('records')" to="/records" />
        <q-breadcrumbs-el :label="record?.token" />
      </q-breadcrumbs>
    </div>
    <q-separator />
    <div class="q-pa-md">
      <div>
        <div class="text-h6 q-mb-sm">{{ t('record.raw_data') }}</div>
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
            header-class="bg-grey-3"
          >
            <q-card>
              <q-card-section>
                <div class="row q-col-gutter-md">
                  <div class="col-12 col-md-6">
                    <fields-list :items="dataItems1" :dbobject="record?.data" />
                  </div>
                  <div class="col-12 col-md-6">
                    <fields-list :items="dataItems2" :dbobject="record?.data" />
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </q-expansion-item>
        </q-list>

        <q-list bordered class="q-mt-md">
          <q-expansion-item
            :label="t('record.typo')"
            icon="commute"
            expand-icon="expand_more"
            header-class="bg-grey-3"
          >
            <q-card>
              <q-card-section>
                <div class="row q-col-gutter-md">
                  <div class="col-12 col-md-6">
                    <div class="text-bold q-mb-sm">{{ t('record.typo_reco') }}</div>
                    <fields-list :items="typoRecoItems" :dbobject="record?.typo?.reco" />
                  </div>
                  <div class="col-12 col-md-6">
                    <div class="text-bold q-mb-sm">{{ t('record.typo_reco_pro') }}</div>
                    <fields-list :items="typoRecoProItems" :dbobject="record?.typo?.reco_pro" />
                    <div class="text-bold q-mb-sm q-mt-lg">{{ t('record.typo_reco_actions') }}</div>
                    <fields-list
                      :items="typoRecoActionsItems"
                      :dbobject="record?.typo?.reco_actions"
                    />
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </q-expansion-item>
        </q-list>
      </div>
      <div>
        <div class="text-h6 q-mb-sm q-mt-lg">{{ t('record.isochrones') }}</div>
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
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import type { Company, Campaign } from 'src/models'
import IsochronesMap from 'src/components/IsochronesMap.vue'
import FieldsList from 'src/components/FieldsList.vue'
import type { FieldItem } from 'src/components/FieldsList.vue'
import type { Record } from 'src/models'
import { notifyError } from 'src/utils/notify'

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
  const recommendations = (record.value?.typo?.reco?.reco_dt2 as string[]) || []
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
          to: `/company/${val.company_id}?campaign=${val.campaign_id}`,
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
    ? Object.keys(record.value.typo.reco).map((key) => ({ field: key }))
    : []
})
const typoRecoProItems = computed<FieldItem[]>(() => {
  return record.value?.typo?.reco_pro
    ? Object.keys(record.value.typo.reco_pro).map((key) => ({ field: key }))
    : []
})
const typoRecoActionsItems = computed<FieldItem[]>(() => {
  return record.value?.typo?.reco_actions
    ? Object.keys(record.value.typo.reco_actions).map((key) => ({ field: key }))
    : []
})
function onInit() {
  recordService
    .get(id.value + '')
    .then((data: Record) => {
      record.value = data
      if (data.company_id) {
        companyService.get(data.company_id + '').then((compData: Company) => {
          company.value = compData
        })
      }
      if (data.campaign_id) {
        campaignService.get(data.campaign_id + '').then((campData: Campaign) => {
          campaign.value = campData
        })
      }
    })
    .catch(() => {
      notifyError(t('error.loading_record'))
      router.push('/records')
    })
}
</script>
