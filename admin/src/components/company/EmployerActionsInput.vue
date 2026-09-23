<template>
  <div>
    <div v-if="label" class="q-mb-sm text-foreground">{{ label }}</div>
    <div v-if="hint">{{ hint }}</div>
    <q-tabs v-model="tab" no-caps align="left">
      <q-tab name="personnal" :label="t('actions.personnal')" />
      <q-tab name="professional" :label="t('actions.professional')" />
    </q-tabs>
    <q-tab-panels v-model="tab">
      <q-tab-panel name="personnal" class="q-pl-none q-pr-none">
        <template v-for="type in Object.keys(actionOptions)" :key="type">
          <q-select
            filled
            multiple
            emit-value
            map-options
            clearable
            v-model="actions[type]"
            :options="actionOptions[type]"
            :label="t(`actions.${type}_label`)"
            :hint="t(`actions.${type}_hint`)"
            @update:model-value="onUpdate(type, $event)"
          >
            <template #option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section>
                  <q-item-label :class="{ 'text-italic': scope.opt.value === NEW_ACTION }">
                    {{ scope.opt.label }}
                  </q-item-label>
                </q-item-section>
              </q-item>
            </template>
          </q-select>
        </template>
      </q-tab-panel>
      <q-tab-panel name="professional" class="q-pl-none q-pr-none">
        <template v-for="type in Object.keys(actionProOptions)" :key="type">
          <q-select
            filled
            multiple
            emit-value
            map-options
            clearable
            v-model="actions[type]"
            :options="actionProOptions[type]"
            :label="t(`actions.${type}_label`)"
            :hint="t(`actions.${type}_hint`)"
            @update:model-value="onUpdate(type, $event)"
          >
            <template #option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section>
                  <q-item-label :class="{ 'text-italic': scope.opt.value === NEW_ACTION }">
                    {{ scope.opt.label }}
                  </q-item-label>
                </q-item-section>
              </q-item>
            </template>
          </q-select>
        </template>
      </q-tab-panel>
    </q-tab-panels>
    <custom-action-dialog
      v-model="showNewActionDialog"
      :company="company"
      :group="newActionGroup"
      @saved="onNewActionSaved"
    />
  </div>
</template>

<script setup lang="ts">
import type { EmployerActions, Company, CompanyAction } from '@/models'
import { notifyError } from '@/utils/notify'
import CustomActionDialog from '@/components/company/CustomActionDialog.vue'

interface Props {
  modelValue: EmployerActions | undefined
  company: Company
  label?: string
  hint?: string
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const { t, locale } = useI18n()
const actionsStore = useActions()

// sentinel option value to trigger the creation of a custom action
const NEW_ACTION = '__new__'

const tab = ref<string>('personnal')
const showNewActionDialog = ref(false)
const newActionGroup = ref('')

function makeDefaultActions(): EmployerActions {
  return {
    mesures_globa: [],
    mesures_tpu: [],
    mesures_train: [],
    mesures_inter: [],
    mesures_velo: [],
    mesures_covoit: [],
    mesures_elec: [],
    mesures_pro_globa: [],
    mesures_pro_velo: [],
    mesures_pro_tpu: [],
    mesures_pro_train: [],
    mesures_pro_elec: [],
  }
}

const actions = ref<EmployerActions>(props.modelValue || makeDefaultActions())

interface Option {
  value: string
  label: string
}

onMounted(onInit)

watch(() => props.modelValue, onInit)

function onInit() {
  actions.value = props.modelValue || makeDefaultActions()
  if (props.company.id) {
    actionsStore.company = props.company
    actionsStore.load().then(removeDeletedActions).catch(notifyError)
  }
}

// remove the custom actions that do not exist anymore from the selection
function removeDeletedActions() {
  let changed = false
  Object.keys(actions.value).forEach((group) => {
    const values = actions.value[group]
    if (!values) return
    const filtered = values.filter((val) => !actionsStore.isDeleted(val, props.company.id))
    if (filtered.length !== values.length) {
      actions.value[group] = filtered
      changed = true
    }
  })
  if (changed) emit('update:modelValue', actions.value)
}

const actionOptions = computed<{ [key: string]: Option[] }>(() => {
  return {
    mesures_globa: makeOptions('mesures_globa', ['budget', 'wfh', 'wftp', 'wfro']),
    mesures_tpu: makeOptions('mesures_tpu', ['tpg_pass', 'lex_pass']),
    mesures_train: makeOptions('mesures_train', ['cff_pass_ag', 'cff_pass_dtp', 'cff_pass_dt']),
    mesures_inter: makeOptions('mesures_inter', ['pnr_pass', 'shuttle', 'velo_station']),
    mesures_velo: makeOptions('mesures_velo', [
      'bike_subs',
      'shower',
      'bike_parking',
      'ebike_charging',
      'bike_equipment',
      'bike_courses',
    ]),
    mesures_covoit: makeOptions('mesures_covoit', [
      'carpool_subs',
      'carpool_connect',
      'carpool_parking',
    ]),
    mesures_elec: makeOptions('mesures_elec', ['ev_charging', 'mobility_pass']),
  }
})

const actionProOptions = computed<{ [key: string]: Option[] }>(() => {
  return {
    mesures_pro_globa: makeOptions('mesures_pro_globa', ['videoconf']),
    mesures_pro_velo: makeOptions('mesures_pro_velo', ['ebike_fleet']),
    mesures_pro_tpu: makeOptions('mesures_pro_tpu', ['tpu_pro', 'tpu_rmb']),
    mesures_pro_train: makeOptions('mesures_pro_train', ['train_pro', 'train_obl', 'train_rmb']),
    mesures_pro_elec: makeOptions('mesures_pro_elec', ['ev_fleet']),
  }
})

function onUpdate(group: string, value: string[] | null) {
  const values = value || []
  if (values.includes(NEW_ACTION)) {
    // do not keep the sentinel in the selection, open the creation dialog instead
    actions.value[group] = values.filter((val) => val !== NEW_ACTION)
    newActionGroup.value = group
    showNewActionDialog.value = true
  }
  emit('update:modelValue', actions.value)
}

function onNewActionSaved(action: CompanyAction) {
  actionsStore
    .load()
    .then(() => {
      // select the newly created action
      const group = action.group
      if (!actions.value[group]) actions.value[group] = []
      actions.value[group].push(`${action.id}`)
      emit('update:modelValue', actions.value)
    })
    .catch(notifyError)
}

function makeOptions(group: string, types: string[]) {
  const opts: Option[] = types.map((type) => ({
    label: t(`actions.${type}`),
    value: type,
  }))
  actionsStore.items
    .filter((item) => item.group === group)
    .forEach((item) => {
      const val = `${item.id}`
      opts.push({
        label: item.labels ? item.labels[locale.value] || item.labels['en'] || val : val,
        value: val,
      })
    })
  if (props.company.id) {
    opts.push({ label: t('actions.add_custom'), value: NEW_ACTION })
  }
  return opts
}
</script>
