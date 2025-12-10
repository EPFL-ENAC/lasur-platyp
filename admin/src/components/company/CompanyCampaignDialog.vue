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
                <q-list bordered separator class="q-mb-md">
                  <q-item v-for="(workplace, index) in selected.workplaces" :key="index">
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
              <q-btn
                size="sm"
                color="primary"
                :label="t('add')"
                icon="add"
                @click="onAddWorkplace"
              />
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
</script>
