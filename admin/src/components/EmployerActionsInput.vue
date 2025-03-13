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
import type { EmployerActions } from 'src/models'
interface Props {
  modelValue: EmployerActions | undefined
  label?: string
  hint?: string
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const { t } = useI18n()

const tab = ref<string>('personnal')

const actions = ref<EmployerActions>(
  props.modelValue || {
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
  },
)

interface Option {
  value: string
  label: string
}

const actionOptions: { [key: string]: Option[] } = {
  mesures_globa: makeOptions(['budget', 'wfh', 'wftp']),
  mesures_tpu: makeOptions(['tpg_pass', 'lex_pass']),
  mesures_train: makeOptions(['cff_pass_ag', 'cff_pass_dtp', 'cff_pass_dt']),
  mesures_inter: makeOptions(['pnr_pass', 'shuttle', 'velo_station']),
  mesures_velo: makeOptions([
    'bike_subs',
    'shower',
    'bike_parking',
    'ebike_charging',
    'bike_equipment',
  ]),
  mesures_covoit: makeOptions(['carpool_subs', 'carpool_connect', 'carpool_parking']),
  mesures_elec: makeOptions(['ev_charging', 'mobility_pass']),
}

const actionProOptions: { [key: string]: Option[] } = {
  mesures_pro_velo: makeOptions(['ebike_fleet']),
  mesures_pro_tpu: makeOptions(['tpu_pro']),
  mesures_pro_train: makeOptions(['train_pro']),
  mesures_pro_elec: makeOptions(['ev_fleet']),
}

function onUpdate() {
  emit('update:modelValue', actions.value)
}

function makeOptions(types: string[]) {
  return types.map((type) => ({
    label: t(`actions.${type}`),
    value: type,
  }))
}
</script>
