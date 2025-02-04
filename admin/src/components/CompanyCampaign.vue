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
    <div class="row q-col-gutter-md q-mb-md">
      <div class="col-12 col-md-6">
        <fields-list :items="items1" :dbobject="item" />
      </div>
      <div class="col-12 col-md-6">
        <fields-list :items="items2" :dbobject="item" />
      </div>
    </div>
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
import FieldsList from 'src/components/FieldsList.vue'
import type { FieldItem } from 'src/components/FieldsList.vue'
import { formatCoordinates } from 'src/utils/numbers'

const { t } = useI18n()
const authStore = useAuthStore()
const campaignsStore = useCampaigns()

interface Props {
  item: Campaign
  company: Company
}
const props = defineProps<Props>()

const showDialog = ref(false)

const items1: FieldItem[] = [
  {
    field: 'name',
  },
  {
    field: 'address',
    label: 'address',
  },
  {
    field: 'lat',
    label: 'location',
    links: () => [
      {
        label: `${formatCoordinates(props.item.lat || 0, props.item.lon || 0)}`,
        to: `https://www.google.com/maps/search/?api=1&query=${props.item.lat},${props.item.lon}`,
        icon: 'location_on',
        //iconRight: 'open_in_new',
      },
    ],
  },
]

const items2: FieldItem[] = [
  {
    field: 'start_date',
    label: 'start_date',
    format: (val: Campaign) => val.start_date?.split('T')[0] || '-',
  },
  {
    field: 'end_date',
    label: 'end_date',
    format: (val: Campaign) => val.end_date?.split('T')[0] || '-',
  },
]

function onEdit() {
  showDialog.value = true
}

function onSaved() {
  campaignsStore.load()
}
</script>
