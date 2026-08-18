<template>
  <q-btn-dropdown color="primary" size="sm" icon="download" :label="t('download')">
    <q-list>
      <q-item clickable v-close-popup @click="onDownload(false)">
        <q-item-section>
          <q-item-label>{{ t('all') }}</q-item-label>
        </q-item-section>
      </q-item>

      <q-item clickable v-close-popup @click="onDownload(true)">
        <q-item-section>
          <q-item-label>{{ t('completed') }}</q-item-label>
        </q-item-section>
      </q-item>
    </q-list>
  </q-btn-dropdown>
</template>

<script setup lang="ts">
import type { Query } from 'src/components/models'
import type { Record } from 'src/models'
import Papa from 'papaparse'
import { useQuasar } from 'quasar'
import MarkdownDialog from 'src/components/MarkdownDialog.vue'

const props = defineProps<{
  filter?: string
  companyFilter?: string[]
  campaignFilter?: string[]
}>()

const { t } = useI18n({ useScope: 'global' })
const services = useServices()
const $q = useQuasar()
const service = services.make('record')

function onDownload(completedOnly: boolean) {
  $q.dialog({
    component: MarkdownDialog,
    componentProps: {
      text: t('database_data_protection_notice.content'),
      title: t('database_data_protection_notice.title'),
      canCancel: true,
    },
    persistent: true,
  }).onOk(() => {
    downloadCSV(completedOnly)
  })
}

function downloadCSV(completedOnly: boolean) {
  const query: Query = {
    $skip: 0,
    $limit: 1000,
  }
  query.filter = {}
  if (props.filter) {
    query.filter = {
      token: { $ilike: `%${props.filter}%` },
    }
  }
  if (completedOnly) {
    query.filter.typo = { $exists: true }
  }
  if (props.companyFilter?.length) {
    query.filter.company_id = { $in: props.companyFilter }
  }
  if (props.campaignFilter?.length) {
    query.filter.campaign_id = { $in: props.campaignFilter }
  }
  service
    .find(query)
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    .then((result: any) => {
      const rows = result.data.map((row: Record) => flattenRow(row))
      const columnsSet: Set<string> = new Set()
      rows.forEach((row: Record) => {
        Object.keys(row).forEach((key) => {
          columnsSet.add(key)
        })
      })
      const columns = Array.from(columnsSet).sort()
      const csv = Papa.unparse(rows, { columns })
      // make browser download the file
      const blob = new Blob([csv], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'records.csv'
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
    })
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function flattenRow(obj: any, prefix = '') {
  const acc: { [key: string]: string } = {}
  return Object.keys(obj).reduce((acc, key: string) => {
    const newKey = prefix ? `${prefix}.${key}` : key
    if (typeof obj[key] === 'object' && obj[key] !== null) {
      Object.assign(acc, flattenRow(obj[key], newKey))
    } else {
      acc[newKey] = obj[key]
    }
    return acc
  }, acc)
}
</script>
