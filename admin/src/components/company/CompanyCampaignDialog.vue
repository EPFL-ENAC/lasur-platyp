<template>
  <q-dialog v-model="showDialog" persistent @hide="onHide">
    <q-card class="dialog-md">
      <q-card-actions>
        <div class="text-h6 q-ml-sm">{{ t(editMode ? 'edit' : 'add') }}</div>
        <q-space />
        <q-btn flat icon="close" color="primary" v-close-popup />
      </q-card-actions>
      <q-separator />

      <q-card-section>
        <q-form ref="form">
          <q-tabs
            v-model="tab"
            dense
            no-caps
            class="text-grey"
            active-color="secondary"
            active-bg-color="grey-4"
            indicator-color="primary"
            align="left"
          >
            <q-tab name="general" :label="t('general')" />
            <q-tab
              name="workplaces"
              :label="t('campaign.workplaces.title')"
              :alert="selected.workplaces?.length ? false : 'negative'"
            />
          </q-tabs>
          <q-separator />
          <q-tab-panels animated v-model="tab">
            <q-tab-panel name="general">
              <q-input
                filled
                v-model="selected.name"
                :label="t('name') + ' *'"
                lazy-rules
                :rules="[(val) => !!val || t('field_required')]"
              />
              <q-input
                filled
                v-model="selected.contact_name"
                :label="t('campaign.contact_name')"
                :hint="t('campaign.contact_name_hint')"
                class="q-mb-md"
              />
              <q-input
                filled
                v-model="selected.contact_email"
                :label="t('campaign.contact_email')"
                :hint="t('campaign.contact_email_hint')"
                lazy-rules
                :rules="[
                  (val) =>
                    !val || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val) || t('valid_email_required'),
                ]"
                class="q-mb-md"
              />
              <q-input
                filled
                v-model="selected.info_url"
                :label="t('campaign.info_url')"
                :hint="t('campaign.info_url_hint')"
                lazy-rules
                :rules="[(val) => !val || /^(http|https):/.test(val) || t('valid_url_required')]"
                class="q-mb-md"
              />
              <q-input
                v-if="editMode"
                filled
                v-model="selected.slug"
                :label="t('campaign.slug') + ' *'"
                :hint="t('campaign.slug_hint')"
                lazy-rules
                :rules="[(val) => !!val || t('field_required')]"
                class="q-mb-md"
              >
                <template v-slot:append>
                  <q-icon
                    name="refresh"
                    class="cursor-pointer"
                    @click="selected.slug = generateSlug()"
                  />
                </template>
              </q-input>
              <q-input
                filled
                v-model="selected.start_date"
                :label="t('start_date')"
                class="q-mb-md"
              >
                <template v-slot:append>
                  <q-icon name="event" class="cursor-pointer">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-date v-model="selected.start_date" mask="YYYY-MM-DD">
                        <div class="row items-center justify-end">
                          <q-btn v-close-popup label="Close" color="primary" flat />
                        </div>
                      </q-date>
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
              <q-input filled v-model="selected.end_date" :label="t('end_date')" class="q-mb-md">
                <template v-slot:append>
                  <q-icon name="event" class="cursor-pointer">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-date v-model="selected.end_date" mask="YYYY-MM-DD">
                        <div class="row items-center justify-end">
                          <q-btn v-close-popup label="Close" color="primary" flat />
                        </div>
                      </q-date>
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
              <q-toggle
                v-model="withActions"
                :label="t('campaign.with_actions')"
                @update:model-value="onWithActionsChanged"
              />
              <employer-actions-input
                v-if="withActions"
                v-model="selected.actions"
                :company="props.company"
                :label="t('company.actions')"
                class="q-mt-lg"
              />
            </q-tab-panel>
            <q-tab-panel name="workplaces">
              <div class="text-hint q-mb-md">
                {{ t('campaign.workplaces.hint') }}
              </div>
              <div v-if="selected.workplaces && selected.workplaces.length > 0">
                <q-list
                  bordered
                  separator
                  class="q-mb-md"
                  style="max-height: 500px; overflow-y: auto"
                >
                  <q-item
                    v-for="(workplace, index) in selected.workplaces"
                    :key="workplace.id || `wp-${index}`"
                  >
                    <q-item-section>
                      <workplace-input
                        v-if="selected.workplaces[index]"
                        v-model="selected.workplaces[index]"
                    /></q-item-section>
                    <q-item-section side>
                      <q-btn
                        flat
                        size="sm"
                        color="negative"
                        icon="delete"
                        class="q-mt-sm"
                        @click="selected.workplaces.splice(index, 1)"
                      />
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>
              <div class="row">
                <q-btn
                  size="sm"
                  color="primary"
                  :label="t('add')"
                  icon="add"
                  @click="onAddWorkplace"
                />
                <q-btn
                  size="sm"
                  color="primary"
                  :label="t('upload_csv')"
                  icon="upload"
                  class="on-right"
                  @click="onUpload"
                />
                <q-btn
                  flat
                  size="sm"
                  color="primary"
                  :label="t('download_csv')"
                  icon="download"
                  class="on-right"
                  @click="onDownload"
                />
              </div>
              <div class="text-hint q-mt-md">
                {{ t('campaign.import_workplaces_hint') }}
              </div>
            </q-tab-panel>
          </q-tab-panels>
        </q-form>
      </q-card-section>

      <q-separator />

      <q-card-actions align="right" class="bg-grey-3">
        <q-btn flat :label="t('cancel')" color="secondary" v-close-popup />
        <q-btn :label="t('save')" color="primary" @click="onSave" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import slug from 'slug'
import type { Campaign, Company, Workplace } from 'src/models'
import { notifyError } from 'src/utils/notify'
import EmployerActionsInput from 'src/components/company/EmployerActionsInput.vue'
import WorkplaceInput from 'src/components/company/WorkplaceInput.vue'
import { generateToken } from 'src/utils/generate'
import Papa from 'papaparse'

interface DialogProps {
  modelValue: boolean
  item: Campaign
  company: Company
}

const props = defineProps<DialogProps>()
const emit = defineEmits(['update:modelValue', 'saved'])

const { t } = useI18n()
const campaignsStore = useCampaigns()

const form = ref()
const showDialog = ref(props.modelValue)
const selected = ref<Campaign>({
  name: '',
} as Campaign)
const withActions = ref(false)
const editMode = ref(false)
const tab = ref('general')

onMounted(() => {
  if (props.modelValue) {
    onInit()
  }
})

watch(
  () => props.modelValue,
  (value) => {
    if (value) {
      onInit()
    }
    showDialog.value = value
  },
)

function onInit() {
  tab.value = 'general'
  // deep copy
  selected.value = JSON.parse(JSON.stringify(props.item))
  selected.value.start_date = selected.value.start_date?.split('T')[0]
  selected.value.end_date = selected.value.end_date?.split('T')[0]
  if (!selected.value.workplaces) {
    selected.value.workplaces = []
  }
  // check if there are some actions selected
  withActions.value =
    Object.keys(selected.value.actions || {}).filter((key) =>
      selected.value.actions && selected.value.actions[key]
        ? selected.value.actions[key].length > 0
        : false,
    ).length > 0
  editMode.value = selected.value.id !== undefined
  if (editMode.value && !selected.value.slug) {
    selected.value.slug = generateSlug()
  }
}

function onHide() {
  showDialog.value = false
  emit('update:modelValue', false)
}

function generateSlug() {
  return slug(props.company.name + ' ' + selected.value.name + ' ' + generateToken(4), {
    lower: true,
  })
}

async function onSave() {
  if (!selected.value.slug) {
    selected.value.slug = generateSlug()
  }
  const valid = await form.value.validate()
  if (!valid) return
  if (selected.value === undefined) return
  if (!selected.value.workplaces || selected.value.workplaces.length === 0) {
    notifyError(t('campaign.workplaces.required'))
    return
  }
  selected.value.start_date =
    selected.value.start_date === '' ? undefined : selected.value.start_date
  selected.value.end_date = selected.value.end_date === '' ? undefined : selected.value.end_date
  if (selected.value.id) {
    campaignsStore.service
      .update(selected.value.id, selected.value)
      .then(() => {
        emit('saved', selected.value)
        onHide()
      })
      .catch(notifyError)
  } else {
    campaignsStore.service
      .create(selected.value)
      .then(() => {
        emit('saved', selected.value)
        onHide()
      })
      .catch(notifyError)
  }
}

function onWithActionsChanged(value: boolean) {
  if (!value) {
    selected.value.actions = {}
  }
}

function onAddWorkplace() {
  if (!selected.value.workplaces) {
    selected.value.workplaces = []
  }
  selected.value.workplaces.push({
    name: '',
    address: '',
    lat: 0,
    lon: 0,
  } as Workplace)
}

function onUpload() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.csv,text/csv'
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  input.onchange = (e: any) => {
    const file = e.target.files[0]
    if (!file) return
    const reader = new FileReader()
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    reader.onload = (event: any) => {
      const csvData = event.target.result
      const results = Papa.parse(csvData, {
        header: true,
        skipEmptyLines: true,
      })
      // check columns
      const requiredColumns = ['name', 'address', 'lat', 'lon']
      const missingColumns = requiredColumns.filter((col) => !results.meta.fields?.includes(col))
      if (missingColumns.length > 0) {
        notifyError(t('campaign.csv_missing_columns', { columns: missingColumns.join(', ') }))
        return
      }
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      results.data.forEach((row: any) => {
        if (!selected.value.workplaces) {
          selected.value.workplaces = []
        }
        if (!row['name'] || !row['address'] || !row['lat'] || !row['lon']) {
          return
        }
        // add or update workplace
        const existingIndex = selected.value.workplaces.findIndex(
          (wp) => wp.name === row['name'] && wp.address === row['address'],
        )
        if (existingIndex !== -1) {
          // update existing workplace
          selected.value.workplaces[existingIndex] = {
            name: row['name'],
            address: row['address'],
            lat: row['lat'] ? parseFloat(row['lat']) : 0,
            lon: row['lon'] ? parseFloat(row['lon']) : 0,
          } as Workplace
          return
        }
        // add new workplace
        selected.value.workplaces.push({
          name: row['name'] || '',
          address: row['address'] || '',
          lat: row['lat'] ? parseFloat(row['lat']) : 0,
          lon: row['lon'] ? parseFloat(row['lon']) : 0,
        } as Workplace)
      })
    }
    reader.readAsText(file)
  }
  input.click()
}

function onDownload() {
  if (!selected.value.workplaces || selected.value.workplaces.length === 0) {
    notifyError(t('campaign.workplaces.required'))
    return
  }
  // use ; as separator for better compatibility with Excel in some locales
  const csvData = Papa.unparse(
    selected.value.workplaces.map((wp) => ({
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
    `${props.company.name}_${selected.value.name}_workplaces.csv`.replaceAll(' ', '_'),
  )
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>
