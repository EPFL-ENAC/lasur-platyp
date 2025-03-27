<template>
  <div>
    <div v-if="rows?.length < 1">
      <q-btn
        size="sm"
        color="secondary"
        :disable="loading"
        :label="t('add')"
        icon="add"
        @click="onAdd"
      />
    </div>
    <q-table
      v-show="rows?.length > 0"
      flat
      ref="tableRef"
      :rows="rows"
      :columns="columns"
      row-key="id"
      v-model:pagination="pagination"
      :loading="loading"
      :filter="filter"
      binary-state-sort
      @request="onRequest"
      :rows-per-page-options="[10, 25, 50]"
    >
      <template v-slot:top>
        <q-btn
          size="sm"
          color="secondary"
          :disable="loading"
          :label="t('add')"
          icon="add"
          @click="onAdd"
        />
        <q-space />
        <q-input dense debounce="300" v-model="filter" clearable>
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
      </template>
      <template v-slot:body-cell-identifier="props">
        <q-td :props="props">
          {{ props.row.identifier }}
        </q-td>
      </template>
      <template v-slot:body-cell-token="props">
        <q-td :props="props">
          <a :href="`${collectUrl}/go/${props.row.token}`" target="_blank"
            >{{ props.row.token }} <q-icon name="open_in_new"></q-icon
          ></a>
          <q-btn
            color="grey-8"
            size="12px"
            flat
            dense
            round
            icon="content_copy"
            class="on-right"
            @click="onTokenCopy(props.row)"
          />
        </q-td>
      </template>
      <template v-slot:body-cell-data="props">
        <q-td :props="props">
          <div class="text-caption">{{ props.row.data }}</div>
        </q-td>
      </template>
      <template v-slot:body-cell-action="props">
        <q-td :props="props">
          <q-btn color="grey-8" size="12px" flat dense round icon="edit" @click="onEdit(props.row)">
          </q-btn>
          <q-btn
            color="grey-8"
            size="12px"
            flat
            dense
            round
            icon="delete"
            @click="onShowRemove(props.row)"
          >
          </q-btn>
        </q-td>
      </template>
    </q-table>
    <confirm-dialog
      v-model="showRemoveDialog"
      :title="t('remove_participant')"
      :text="t('remove_participant_text', { identifier: selected.identifier })"
      @confirm="onRemove()"
    />
    <participant-dialog
      v-if="selected"
      v-model="showParticipantDialog"
      :item="selected"
      @saved="onSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { copyToClipboard } from 'quasar'
import type { Campaign, Participant } from 'src/models'
import type { PaginationOptions } from 'src/utils/pagination'
import { notifyError, notifyInfo } from 'src/utils/notify'
import ParticipantDialog from 'src/components/ParticipantDialog.vue'
import { DefaultAlignment, type Query } from 'src/components/models'
import { makePaginationRequestHandler } from 'src/utils/pagination'
import ConfirmDialog from 'src/components/ConfirmDialog.vue'
import { collectUrl } from 'src/boot/api'

const { t } = useI18n()
const participantsStore = useParticipants()

interface Props {
  campaign: Campaign
}
const props = defineProps<Props>()

const rows = ref<Participant[]>([])
const showRemoveDialog = ref(false)
const showParticipantDialog = ref(false)
const selected = ref<Participant>({} as Participant)
const tableRef = ref()
const filter = ref('')
const loading = ref(false)
const pagination = ref<PaginationOptions>({
  sortBy: 'identifier',
  descending: false,
  page: 1,
  rowsPerPage: 10,
})

const columns = computed(() => {
  const cols = [
    {
      name: 'identifier',
      required: true,
      label: t('identifier'),
      align: DefaultAlignment,
      field: 'identifier',
      sortable: true,
    },
    {
      name: 'token',
      required: true,
      label: t('token'),
      align: DefaultAlignment,
      field: 'token',
      sortable: true,
    },
    {
      name: 'status',
      required: true,
      label: t('status'),
      align: DefaultAlignment,
      field: 'status',
      sortable: true,
    },
    {
      name: 'data',
      required: true,
      label: t('data'),
      align: DefaultAlignment,
      field: 'data',
      sortable: false,
    },
    {
      name: 'action',
      align: DefaultAlignment,
      label: '',
      required: false,
      field: 'action',
      sortable: false,
    },
  ]
  return cols
})

onMounted(onInit)

watch(
  () => props.campaign,
  () => {
    onInit()
  },
)

function onInit() {
  participantsStore.campaign = props.campaign
  tableRef.value.requestServerInteraction()
}
function fetchFromServer(
  startRow: number,
  count: number,
  filter: string,
  sortBy: string,
  descending: boolean,
) {
  const query: Query = {
    $skip: startRow,
    $limit: count,
    $sort: [sortBy, descending],
  }
  query.filter = {
    campaign_id: { $eq: props.campaign.id },
  }
  if (filter) {
    query.filter = {
      $and: [query.filter, { identifier: { $ilike: `%${filter}%` } }],
    }
  }
  return (
    participantsStore.service
      .find(query)
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      .then((result: any) => {
        rows.value = result.data
        loading.value = false
        return result
      })
  )
}

const onRequest = makePaginationRequestHandler(fetchFromServer, pagination)

function onAdd() {
  selected.value = {
    campaign_id: props.campaign.id,
    data: {
      company_vehicle: false,
    },
  } as Participant
  showParticipantDialog.value = true
}

function onEdit(item: Participant) {
  selected.value = { ...item }
  showParticipantDialog.value = true
}

function onSaved() {
  onInit()
}

function onShowRemove(item: Participant) {
  selected.value = item
  showRemoveDialog.value = true
}

function onRemove() {
  if (selected.value.id === undefined) return
  participantsStore.service
    .remove(selected.value.id)
    .then(() => {
      onInit()
    })
    .catch(notifyError)
}

function onTokenCopy(item: Participant) {
  if (!item.token) return
  copyToClipboard(`${collectUrl}/go/${item.token}`)
  notifyInfo(t('link_copied'))
}
</script>
