<template>
  <div>
    <q-card flat class="q-ma-md">
      <q-card-section>
        <h5 class="text-h5 q-ma-none">{{ t('overview') }}</h5>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <campaign-charts :item="item" />
      </q-card-section>

      <q-separator />

      <q-card-actions align="right">
        <q-btn
          v-if="isCompanyAdmin"
          :label="t('report')"
          size="sm"
          color="primary"
          icon="bar_chart"
          @click="onShowStats"
        />
      </q-card-actions>
    </q-card>

    <q-card flat class="q-ma-md">
      <q-card-section>
        <h5 class="text-h5 q-ma-none">{{ t('overview') }}</h5>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <div class="row q-col-gutter-md q-mb-md">
          <div class="col-12 col-md-6">
            <fields-list :items="items1" :dbobject="item" />
          </div>
          <div class="col-12 col-md-6">
            <fields-list :items="items2" :dbobject="item" />
          </div>
        </div>
        <div v-if="hasActions">
          <div class="q-mb-sm">{{ t('company.actions') }}</div>
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
      </q-card-section>
    </q-card>

    <q-card flat class="q-ma-md">
      <q-card-section>
        <h5 class="text-h5 q-ma-none">
          {{ t('campaign.workplaces.title') }}
          <q-badge color="primary" class="on-right">{{ workplacesCount }}</q-badge>
        </h5>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <div>
          <q-icon
            :name="item.open_workplaces ? 'check_box' : 'check_box_outline_blank'"
            size="sm"
            class="q-mr-sm"
          />
          <span class="q-mt-xs">{{ t('campaign.workplaces.open_workplaces') }}</span>
        </div>
        <div>
          <div v-for="(wp, index) in visibleWorkplaces" :key="index" class="workplace">
            <div class="text-overline text-half-muted workplace-name">{{ wp.name }}</div>
            <div class="workplace-address">
              <div>{{ wp.address }}</div>
              <div class="q-mt-sm">
                <a
                  :href="`https://www.google.com/maps/search/?api=1&query=${wp.lat},${wp.lon}`"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <q-icon name="location_on" class="q-mr-xs" />
                  <span>{{ formatCoordinates(wp.lat, wp.lon) }}</span>
                </a>
              </div>
            </div>
            <div class="workplace-isochrone">
              <q-expansion-item
                :label="t('campaign.workplaces.show_isochrone')"
                icon="map"
                expand-icon="expand_more"
                header-class="bg-super-muted"
              >
                <div class="q-pa-sm">
                  <isochrones-map
                    :mapId="`map-workplace-${index}`"
                    :center="[wp.lon, wp.lat]"
                    :reco="wp.address"
                    height="400px"
                  />
                </div>
              </q-expansion-item>
            </div>
          </div>
        </div>
        <div class="row q-mt-sm">
          <q-btn
            v-if="hasMoreWorkplaces"
            flat
            no-caps
            size="sm"
            color="primary"
            :label="t('show_more')"
            icon="expand_more"
            @click="shownWorkplaces = workplacesCount"
          />
          <q-btn
            v-else-if="shownWorkplaces > SHOW_WORKPLACES_MIN"
            flat
            no-caps
            size="sm"
            color="primary"
            :label="t('show_less')"
            icon="expand_less"
            @click="shownWorkplaces = SHOW_WORKPLACES_MIN"
          />
        </div>
      </q-card-section>

      <q-separator />

      <q-card-actions align="right">
        <q-btn
          v-if="workplacesCount > 0"
          size="sm"
          color="primary"
          :label="t('download_csv')"
          icon="download"
          class="on-right"
          @click="onDownloadWorkplaces"
        />
      </q-card-actions>
    </q-card>

    <q-card flat class="q-ma-md">
      <q-card-section>
        <h5 class="text-h5 q-ma-none">{{ t('participants') }}</h5>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <div class="text-hint q-mb-sm">
          {{ t('participants_campaign_hint') }}
        </div>
        <div class="q-mb-lg">
          <q-btn
            v-if="item.slug"
            size="sm"
            color="primary"
            icon-right="content_copy"
            :label="t('survey_link')"
            no-caps
            @click="onSurveyLinkCopy"
          />
          <q-btn
            v-if="isCompanyAdmin"
            :label="t('campaign.email_template.buttonText')"
            outline
            size="sm"
            color="field"
            icon="email"
            class="q-ml-md"
            @click="onShowEmailTemplate"
          />
        </div>
        <div class="text-hint q-mb-md">
          {{ t('participants_individual_hint') }}
        </div>
        <company-campaign-participants :campaign="item" :company="props.company" />
      </q-card-section>
    </q-card>

    <company-charts-dialog
      v-if="props.company"
      v-model="showChartsDialog"
      :company="company"
      :campaign="item"
    />
    <email-template-dialog v-if="props.item" v-model="showEmailTemplateDialog" :campaign="item" />
  </div>
</template>

<script setup lang="ts">
import { copyToClipboard } from 'quasar'
import type { Campaign, Company, EmployerActions } from 'src/models'
import CampaignCharts from 'src/components/charts/CampaignCharts.vue'
import CompanyCampaignParticipants from 'src/components/company/CompanyCampaignParticipants.vue'
import CompanyChartsDialog from 'src/components/company/CompanyChartsDialog.vue'
import FieldsList from 'src/components/FieldsList.vue'
import IsochronesMap from 'src/components/IsochronesMap.vue'
import EmailTemplateDialog from 'src/components/EmailTemplateDialog.vue'
import type { FieldItem } from 'src/components/FieldsList.vue'
import { formatCoordinates } from 'src/utils/numbers'
import { notifyInfo } from 'src/utils/notify'
import { actionItems, actionProItems } from 'src/utils/options'
import Papa from 'papaparse'
import { makeSurveyLink } from 'src/utils/links'

const { t, locale } = useI18n()
const authStore = useAuthStore()
const actionsStore = useActions()

interface Props {
  item: Campaign
  company: Company
}
const props = defineProps<Props>()

const SHOW_WORKPLACES_MIN = 5

const showChartsDialog = ref(false)
const showEmailTemplateDialog = ref(false)
const shownWorkplaces = ref<number>(SHOW_WORKPLACES_MIN)

const isCompanyAdmin = computed(() => {
  if (!props.company) return false
  return authStore.isAdmin || props.company.administrators?.includes(authStore.profile?.email || '')
})

const visibleWorkplaces = computed(() => {
  let wps = props.item.workplaces ? [...props.item.workplaces] : []
  // sort by name
  wps.sort((a, b) => a.name.localeCompare(b.name))
  wps = wps.slice(0, shownWorkplaces.value)
  return wps
})
const hasMoreWorkplaces = computed(() => {
  return props.item.workplaces ? props.item.workplaces.length > shownWorkplaces.value : false
})
const workplacesCount = computed(() => {
  return props.item.workplaces ? props.item.workplaces.length : 0
})

const hasActions = computed(
  () =>
    Object.keys(props.item.actions || {}).filter((key) =>
      props.item.actions && props.item.actions[key] ? props.item.actions[key].length > 0 : false,
    ).length > 0,
)

const formattedActions = computed(() => {
  const allActions: EmployerActions = {}
  if (props.item.actions) {
    Object.keys(props.item.actions).forEach((group) => {
      allActions[group] =
        props.item.actions && props.item.actions[group]
          ? props.item.actions[group].map((action) => {
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

const items1: FieldItem[] = [
  {
    field: 'name',
  },
  {
    field: 'contact_name',
    label: 'campaign.contact_name',
  },
  {
    field: 'contact_email',
    label: 'campaign.contact_email',
  },
  {
    field: 'info_url',
    label: 'campaign.info_url',
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
  {
    field: 'nb_employees',
    label: 'campaign.nb_employees',
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
  {
    field: 'slug',
    label: 'campaign.slug',
    links: () => [
      {
        label: `${props.item.slug}`,
        to: makeSurveyLink(props.item.slug!),
        iconRight: 'open_in_new',
      },
    ],
  },
]

function onSurveyLinkCopy() {
  if (!props.item.slug) return
  copyToClipboard(makeSurveyLink(props.item.slug!))
  notifyInfo(t('survey_link_copied'))
}

function onShowStats() {
  showChartsDialog.value = true
}

function onShowEmailTemplate() {
  showEmailTemplateDialog.value = true
}

function onDownloadWorkplaces() {
  if (!props.item.workplaces || props.item.workplaces.length === 0) {
    notifyInfo(t('company.no_workplaces_to_download'))
    return
  }
  // use ; as separator for better compatibility with Excel in some locales
  const csvData = Papa.unparse(
    props.item.workplaces.map((wp) => ({
      name: wp.name,
      address: wp.address,
      lat: wp.lat,
      lon: wp.lon,
    })),
    { delimiter: ';' },
  )
  const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute(
    'download',
    `${props.company.name}_${props.item.name}_workplaces.csv`.replaceAll(' ', '_'),
  )
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

<style scoped>
.workplace {
  padding: 1rem 0.5rem;

  display: grid;
  grid-template-areas:
    'workplace-name workplace-address'
    'workplace-isochrone workplace-isochrone';

  gap: 1rem;

  border-bottom: 1px solid var(--secondary-border-color);
}

.workplace-name {
  grid-area: workplace-name;
}

.workplace-address {
  grid-area: workplace-address;
}

.workplace-isochrone {
  grid-area: workplace-isochrone;
}
</style>
