<template>
  <div>
    <div class="q-mb-sm text-grey-8">{{ label }}</div>
    <div>{{ hint }}</div>
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
            @update:model-value="onUpdate"
          />
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
            @update:model-value="onUpdate"
          />
        </template>
      </q-tab-panel>
    </q-tab-panels>
  </div>
</template>

<script setup lang="ts">
import type { EmployerActions, Company } from 'src/models'
import { notifyError } from 'src/utils/notify'

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

const tab = ref<string>('personnal')

const defaultActions = {
  mesures_globa: [],
  mesures_tpu: [],
  mesures_train: [],
  mesures_inter: [],
  mesures_velo: [],
  mesures_covoit: [],
  mesures_elec: [],
  mesures_pro_velo: [],
  mesures_pro_tpu: [],
  mesures_pro_train: [],
  mesures_pro_elec: [],
}

const actions = ref<EmployerActions>(props.modelValue || defaultActions)

interface Option {
  value: string
  label: string
}

onMounted(onInit)

watch(() => props.modelValue, onInit)

function onInit() {
  if (props.company.id) {
    actionsStore.company = props.company
    actionsStore.load().catch(notifyError)
  } else {
    actions.value = defaultActions
  }
}

const actionOptions = computed<{ [key: string]: Option[] }>(() => {
  return {
    mesures_globa: makeOptions('mesures_globa', ['budget', 'wfh', 'wftp']),
    mesures_tpu: makeOptions('mesures_tpu', ['tpg_pass', 'lex_pass']),
    mesures_train: makeOptions('mesures_train', ['cff_pass_ag', 'cff_pass_dtp', 'cff_pass_dt']),
    mesures_inter: makeOptions('mesures_inter', ['pnr_pass', 'shuttle', 'velo_station']),
    mesures_velo: makeOptions('mesures_velo', [
      'bike_subs',
      'shower',
      'bike_parking',
      'ebike_charging',
      'bike_equipment',
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
    mesures_pro_velo: makeOptions('mesures_pro_velo', ['ebike_fleet']),
    mesures_pro_tpu: makeOptions('mesures_pro_tpu', ['tpu_pro']),
    mesures_pro_train: makeOptions('mesures_pro_train', ['train_pro']),
    mesures_pro_elec: makeOptions('mesures_pro_elec', ['ev_fleet']),
  }
})

function onUpdate() {
  emit('update:modelValue', actions.value)
}

function makeOptions(group: string, types: string[]) {
  const opts = types.map((type) => ({
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
  return opts
}
</script>
