<template>
  <q-dialog v-model="showDialog" persistent @hide="onHide">
    <q-card class="dialog-md">
      <q-card-section>
        <div class="text-h6">{{ t('company.custom_actions') }}</div>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <span class="text-hint">{{ t('company.custom_actions_hint') }}</span>
      </q-card-section>
      <q-card-section>
        <q-form ref="form">
          <q-list v-if="actions.length" bordered separator class="q-mb-md">
            <q-item v-for="(action, idx) in actions" :key="idx">
              <q-item-section>
                <div class="q-mt-md">
                  <q-select
                    filled
                    v-model="action.group"
                    :label="t('group')"
                    :options="actionGroupOptions"
                    emit-value
                    map-options
                    class="q-mb-md"
                  />
                </div>
                <div>
                  <q-input
                    filled
                    v-model="action.labelEn"
                    :label="t('label_en') + ' *'"
                    lazy-rules
                    :rules="[(val) => !!val || t('field_required')]"
                  />
                </div>
                <div>
                  <q-input
                    filled
                    v-model="action.labelFr"
                    :label="t('label_fr') + ' *'"
                    lazy-rules
                    :rules="[(val) => !!val || t('field_required')]"
                  />
                </div>
              </q-item-section>
              <q-item-section avatar>
                <q-btn
                  icon="delete"
                  rounded
                  dense
                  flat
                  color="negative"
                  size="12px"
                  @click="onDeleteAction(idx)"
                />
              </q-item-section>
            </q-item>
          </q-list>
        </q-form>
        <q-toolbar>
          <q-select
            filled
            dense
            v-model="newAction.group"
            :label="t('group')"
            :options="actionGroupOptions"
            emit-value
            map-options
            style="min-width: 300px"
          />
          <q-btn
            icon="add"
            size="sm"
            color="primary"
            :label="t('add')"
            :disable="newAction.group === ''"
            @click="actions.push(JSON.parse(JSON.stringify(newAction)))"
            class="on-right"
          />
        </q-toolbar>
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
import type { Company, CompanyAction } from 'src/models'
import { actionGroupOptions } from 'src/utils/options'
import { notifyError } from 'src/utils/notify'

const { t } = useI18n()
const actionsStore = useActions()

interface DialogProps {
  modelValue: boolean
  company: Company
}

interface CustomCompanyAction {
  id?: number
  group: string
  labelEn?: string
  labelFr?: string
  company_id: number
}

const props = defineProps<DialogProps>()
const emit = defineEmits(['update:modelValue', 'saved'])

const showDialog = ref(props.modelValue)
const form = ref()
const actions = ref<CustomCompanyAction[]>([])
const newAction = ref<CustomCompanyAction>({
  group: actionGroupOptions[0] ? actionGroupOptions[0].value : '',
  labelEn: '',
  labelFr: '',
  company_id: props.company.id as number,
})

watch(
  () => props.modelValue,
  (value) => {
    showDialog.value = value
    if (value) {
      actions.value = []
      actionsStore.company = props.company
      actionsStore
        .load()
        .then(() => {
          // deep copy
          actions.value = actionsStore.items.map((action) => {
            return {
              id: action.id,
              group: action.group,
              labelEn: action.labels ? action.labels['en'] || '' : '',
              labelFr: action.labels ? action.labels['fr'] || '' : '',
            } as CustomCompanyAction
          })
          newAction.value = {
            group: actionGroupOptions[0] ? actionGroupOptions[0].value : '',
            labelEn: '',
            labelFr: '',
            company_id: props.company.id as number,
          }
        })
        .catch(notifyError)
    }
  },
)

function onHide() {
  showDialog.value = false
  emit('update:modelValue', false)
}

async function onSave() {
  const valid = await form.value.validate()
  if (!valid) return
  if (actions.value === undefined) return
  // make company actions
  const updatedCompanyActions = actions.value
    .filter((action) => action.id)
    .map((action) => {
      return {
        id: action.id,
        group: action.group,
        labels: {
          en: action.labelEn,
          fr: action.labelFr,
        },
        company_id: props.company.id,
      } as CompanyAction
    })
  const newCompanyActions = actions.value
    .filter((action) => action.id === undefined)
    .map((action) => {
      return {
        id: action.id,
        group: action.group,
        labels: {
          en: action.labelEn,
          fr: action.labelFr,
        },
        company_id: props.company.id,
      } as CompanyAction
    })
  const deletedCompanyActionIds = actionsStore.items
    .filter((action) => {
      return !actions.value.some((a) => a.id === action.id)
    })
    .map((action) => action.id)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const promises: Promise<any>[] = []
  // remove deleted actions
  deletedCompanyActionIds.forEach((id) => promises.push(actionsStore.service.remove(id as number)))
  updatedCompanyActions.forEach((action) => {
    promises.push(actionsStore.service.update(action.id as number, action))
  })
  newCompanyActions.forEach((action) => {
    promises.push(actionsStore.service.create(action))
  })
  Promise.all(promises)
    .then(() => {
      emit('saved', true)
      onHide()
    })
    .catch(notifyError)
}

function onDeleteAction(idx: number) {
  actions.value.splice(idx, 1)
}
</script>
