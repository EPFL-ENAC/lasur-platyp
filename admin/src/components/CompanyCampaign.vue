<template>
  <div>
    <q-btn
      v-if="authStore.isAdmin"
      size="sm"
      color="secondary"
      icon="edit"
      class="q-mb-md"
      @click="onEdit"
    />
    <q-btn
      v-if="authStore.isAdmin"
      flat
      size="sm"
      color="negative"
      icon="delete"
      class="q-mb-md on-right"
      @click="onShowRemove"
    />
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
    <div class="text-h6 q-mb-sm">{{ t('participants') }}</div>
    <div class="text-hint q-mb-sm">
      {{ t('participants_campaign_hint') }}
    </div>
    <div class="q-mb-lg">
      <q-btn
        v-if="item.slug"
        size="sm"
        color="accent"
        icon-right="content_copy"
        :label="t('survey_link')"
        no-caps
        @click="onSurveyLinkCopy"
      />
    </div>
    <div class="text-hint q-mb-md">
      {{ t('participants_individual_hint') }}
    </div>
    <company-campaign-participants :campaign="item" />

    <company-campaign-dialog
      v-if="props.company"
      v-model="showDialog"
      :item="props.item"
      :company="props.company"
      @saved="onSaved"
    />
    <confirm-dialog
      v-model="showRemoveDialog"
      :title="t('remove_campaign')"
      :text="t('remove_campaign_text', { name: props.item.name })"
      @confirm="onRemove"
    />
  </div>
</template>

<script setup lang="ts">
import { copyToClipboard } from 'quasar'
import type { Campaign, Company, EmployerActions } from 'src/models'
import CompanyCampaignDialog from 'src/components/CompanyCampaignDialog.vue'
import CompanyCampaignParticipants from 'src/components/CompanyCampaignParticipants.vue'
import ConfirmDialog from 'src/components/ConfirmDialog.vue'
import FieldsList from 'src/components/FieldsList.vue'
import type { FieldItem } from 'src/components/FieldsList.vue'
import { formatCoordinates } from 'src/utils/numbers'
import { collectUrl } from 'src/boot/api'
import { notifyInfo } from 'src/utils/notify'
import { actionItems, actionProItems } from 'src/utils/options'

const { t, locale } = useI18n()
const authStore = useAuthStore()
const campaignsStore = useCampaigns()
const actionsStore = useActions()

interface Props {
  item: Campaign
  company: Company
}
const props = defineProps<Props>()

const showDialog = ref(false)
const showRemoveDialog = ref(false)

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
  {
    field: 'slug',
    label: 'slug',
    links: () => [
      {
        label: `${props.item.slug}`,
        to: `${collectUrl}/go/${props.item.slug}`,
        iconRight: 'open_in_new',
      },
    ],
  },
]

function onEdit() {
  showDialog.value = true
}

function onSaved() {
  campaignsStore.load()
}

function onShowRemove() {
  showRemoveDialog.value = true
}

function onRemove() {
  if (!props.item.id) return
  campaignsStore.service.remove(props.item.id).then(() => {
    campaignsStore.load()
  })
}

function onSurveyLinkCopy() {
  if (!props.item.slug) return
  copyToClipboard(`${collectUrl}/go/${props.item.slug}`)
  notifyInfo(t('survey_link_copied'))
}
</script>
