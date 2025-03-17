<template>
  <q-page>
    <div class="text-h5 q-pa-md">{{ t('records') }}</div>
    <q-separator />
    <div class="q-pa-md">
      <q-table
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
          <q-space />
          <q-input dense debounce="300" v-model="filter" clearable>
            <template v-slot:append>
              <q-icon name="search" />
            </template>
          </q-input>
        </template>
        <template v-slot:body-cell-token="props">
          <q-td :props="props">
            <router-link :to="`/record/${props.row.id}`" class="modus">{{
              props.row.token
            }}</router-link>
          </q-td>
        </template>
        <template v-slot:body-cell-recommendations="props">
          <q-td :props="props">
            <template v-for="reco in getRecoDt2(props.row)" :key="reco">
              <q-chip :label="reco" color="primary" class="text-white" />
            </template>
          </q-td>
        </template>
        <template v-slot:body-cell-action="props">
          <q-td :props="props">
            <q-btn
              color="grey-8"
              size="12px"
              flat
              dense
              round
              icon="visibility"
              :to="`/record/${props.row.id}`"
            >
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
        v-if="selected"
        v-model="showRemoveDialog"
        :title="t('remove_record')"
        :text="t('remove_record_text', { token: selected.token })"
        @confirm="onRemove"
      />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { DefaultAlignment, type Query } from 'src/components/models'
import type { Record } from 'src/models'
import ConfirmDialog from 'src/components/ConfirmDialog.vue'
import { makePaginationRequestHandler } from 'src/utils/pagination'
import type { PaginationOptions } from 'src/utils/pagination'
import { notifyError } from 'src/utils/notify'

const { t } = useI18n({ useScope: 'global' })
const authStore = useAuthStore()
const services = useServices()
const service = services.make('record')

const columns = computed(() => {
  const cols = [
    {
      name: 'id',
      required: true,
      label: 'ID',
      align: DefaultAlignment,
      field: 'id',
      style: 'width: 20px',
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
      name: 'recommendations',
      required: true,
      label: t('recommendations'),
      align: DefaultAlignment,
      field: 'typo',
      sortable: true,
    },
    {
      name: 'updated_at',
      required: true,
      label: t('last_modified'),
      align: DefaultAlignment,
      field: (row: Record) => {
        const date = new Date(row.updated_at || row.created_at || '')
        return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`
      },
      sortable: true,
    },
  ]

  if (authStore.isAdmin) {
    cols.push({
      name: 'action',
      align: DefaultAlignment,
      label: t('action'),
      required: false,
      field: 'action',
      sortable: false,
    })
  }

  return cols
})

const selected = ref<Record>()
const showRemoveDialog = ref(false)
const tableRef = ref()
const rows = ref<Record[]>([])
const types = ref<string[] | null>(null)
const filter = ref('')
const loading = ref(false)
const pagination = ref<PaginationOptions>({
  sortBy: 'token',
  descending: false,
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 10,
})

onMounted(() => {
  tableRef.value.requestServerInteraction()
})

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
  query.filter = {}
  if (types.value?.length) {
    query.filter.$or = types.value.map((val) => {
      return {
        type: {
          $like: val,
        },
      }
    })
  }
  if (filter) {
    const criterion = {
      token: { $ilike: `%${filter}%` },
    }
    if (query.filter.$or) {
      const typesClause = query.filter.$or
      delete query.filter.$or
      query.filter.$and = [{ $or: typesClause }, criterion]
    } else query.filter = criterion
  }
  return (
    service
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

function onShowRemove(item: Record) {
  selected.value = { ...item }
  showRemoveDialog.value = true
}

function onRemove() {
  if (!selected.value?.id) return
  service
    .remove(selected.value.id)
    .then(() => {
      tableRef.value.requestServerInteraction()
    })
    .catch(notifyError)
}

function getRecoDt2(row: Record): string[] {
  return (row.typo?.reco?.reco_dt2 as string[]) || []
}
</script>
