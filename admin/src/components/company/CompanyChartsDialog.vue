<template>
  <q-dialog v-model="showDialog" persistent @hide="onHide" style="min-height: 500px">
    <q-card class="dialog-lg">
      <q-card-section>
        <q-toolbar>
          <q-toolbar-title>
            <span>{{ company?.name }}</span>
            <span v-if="campaign"> - {{ campaign?.name }}</span>
          </q-toolbar-title>
          <q-btn flat icon="map" @click="showMapFilter = true">
            <q-badge v-if="areaCount > 0" color="orange" floating rounded />
          </q-btn>
        </q-toolbar>
      </q-card-section>
      <q-separator />
      <q-card-section>
        <charts-carousel v-if="!stats.loading" :percent="true" :height="500" />
        <div v-else class="row justify-center">
          <q-spinner-dots color="primary" size="50px" />
        </div>
      </q-card-section>
      <q-card-actions align="right" class="bg-grey-3">
        <q-btn flat :label="t('close')" color="secondary" v-close-popup />
      </q-card-actions>
    </q-card>
    <area-dialog
      v-model="showMapFilter"
      :title="`${t('map_filter.workplaces.title')} - ${company?.name} ${campaign ? `- ${campaign.name}` : ''}`"
      :text="t('map_filter.workplaces.hint')"
      :points="campaignsPoints"
      @select="onWorkplacesFilter"
    />
  </q-dialog>
</template>
<script setup lang="ts">
import ChartsCarousel from 'src/components/charts/ChartsCarousel.vue'
import AreaDialog from 'src/components/AreaDialog.vue'
import type { Campaign, Company } from 'src/models'
import type { Filter } from 'src/components/models'
import type { Position } from 'geojson'

interface DialogProps {
  modelValue: boolean
  company: Company
  campaign?: Campaign
}

const props = defineProps<DialogProps>()
const emit = defineEmits(['update:modelValue'])

const stats = useStats()
const showDialog = ref(props.modelValue)
const showMapFilter = ref(false)
const { t } = useI18n()
const campaignsStore = useCampaigns()

const areaFilter = ref<GeoJSON.FeatureCollection | undefined>(undefined)
const areaCount = computed(() => {
  if (areaFilter.value && areaFilter.value.features.length > 0) {
    return areaFilter.value.features.length
  }
  return 0
})

const campaignsPoints = computed<Position[]>(() => {
  const points: Position[] = []
  if (props.campaign) {
    props.campaign.workplaces?.forEach((workplace) => {
      if (workplace.lon && workplace.lat) {
        points.push([workplace.lon, workplace.lat] as Position)
      }
    })
  } else {
    campaignsStore.items?.forEach((campaign) => {
      campaign.workplaces?.forEach((workplace) => {
        if (workplace.lon && workplace.lat) {
          points.push([workplace.lon, workplace.lat] as Position)
        }
      })
    })
  }
  return points
})

watch(
  () => props.modelValue,
  (value) => {
    showDialog.value = value
    if (!value) {
      return
    }
    onQuery()
  },
)

function onQuery() {
  const query = {
    company_id: { $eq: props.company.id },
  } as Filter
  if (props.campaign) {
    query.campaign_id = { $eq: props.campaign.id }
  }
  if (areaFilter.value && areaFilter.value.features.length > 0) {
    query.workplace_location = {
      $geoWithin: {
        $geometry: areaFilter.value.features[0]?.geometry,
      },
    }
  }
  stats.loadStats(query).catch(() => {})
}

function onHide() {
  showDialog.value = false
  emit('update:modelValue', false)
}

function onWorkplacesFilter(area: GeoJSON.FeatureCollection | undefined) {
  areaFilter.value = area
  onQuery()
}
</script>
