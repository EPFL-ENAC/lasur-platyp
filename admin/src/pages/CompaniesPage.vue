<template>
  <q-page>
    <div class="text-h5 q-pa-md">{{ t('companies') }}</div>
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
          <q-btn
            v-if="authStore.isAdmin"
            size="sm"
            color="primary"
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
        <template v-slot:body-cell-name="props">
          <q-td :props="props">
            <router-link :to="`/company/${props.row.id}`" class="modus">{{
              props.row.name
            }}</router-link>
          </q-td>
        </template>
        <template v-slot:body-cell-administrators="props">
          <q-td :props="props">
            <q-badge color="accent" :label="props.row.administrators.length || 0" />
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
              :to="`/company/${props.row.id}`"
            >
            </q-btn>
            <q-btn
              color="grey-8"
              size="12px"
              flat
              dense
              round
              icon="edit"
              @click="onEdit(props.row)"
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

      <company-dialog v-model="showEditDialog" :item="selected" @saved="onSaved"></company-dialog>
      <confirm-dialog
        v-if="selected"
        v-model="showRemoveDialog"
        :title="t('remove_company')"
        :text="t('remove_company_text', { name: selected.name })"
        @confirm="onRemove"
      />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { DefaultAlignment, type Query } from 'src/components/models'
import type { Company } from 'src/models'
import CompanyDialog from 'src/components/CompanyDialog.vue'
import ConfirmDialog from 'src/components/ConfirmDialog.vue'
import { makePaginationRequestHandler } from 'src/utils/pagination'
import type { PaginationOptions } from 'src/utils/pagination'
import { notifyError } from 'src/utils/notify'

const { t } = useI18n({ useScope: 'global' })
const authStore = useAuthStore()
const services = useServices()
const service = services.make('company')

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
      name: 'name',
      required: true,
      label: t('name'),
      align: DefaultAlignment,
      field: 'name',
      sortable: true,
    },
    {
      name: 'administrators',
      required: true,
      label: t('company.administrators'),
      align: DefaultAlignment,
      field: 'administrators',
      sortable: true,
    },
    {
      name: 'updated_at',
      required: true,
      label: t('last_modified'),
      align: DefaultAlignment,
      field: (row: Company) => {
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
      label: '',
      required: false,
      field: 'action',
      sortable: false,
    })
  }

  return cols
})

const selected = ref<Company>()
const showRemoveDialog = ref(false)
const showEditDialog = ref(false)
const tableRef = ref()
const rows = ref<Company[]>([])
const types = ref<string[] | null>(null)
const filter = ref('')
const loading = ref(false)
const pagination = ref<PaginationOptions>({
  sortBy: 'name',
  descending: false,
  page: 1,
  rowsPerPage: 10,
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
      name: { $ilike: `%${filter}%` },
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

function onAdd() {
  selected.value = { name: '', administrators: [] }
  showEditDialog.value = true
}

function onEdit(item: Company) {
  selected.value = { ...item }
  showEditDialog.value = true
}

function onShowRemove(item: Company) {
  selected.value = { ...item }
  showRemoveDialog.value = true
}

function onSaved() {
  tableRef.value.requestServerInteraction()
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
</script>
