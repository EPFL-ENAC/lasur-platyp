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
        <q-list v-if="actions.length" bordered separator class="q-mb-md">
          <q-item v-for="(action, idx) in actions" :key="idx">
            <q-item-section>
              <q-toolbar class="q-pt-md">
                <q-input
                  filled
                  dense
                  v-model="action.name"
                  :label="t('name') + ' *'"
                  lazy-rules
                  :rules="[(val) => !!val || t('field_required')]"
                />
                <q-select
                  filled
                  dense
                  v-model="action.group"
                  :label="t('type') + ' *'"
                  :options="actionGroupOptions"
                  class="on-right"
                  style="min-width: 200px"
                  :rules="[(val) => !!val || t('field_required')]"
                />
              </q-toolbar>
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
        <q-toolbar>
          <q-input
            filled
            dense
            v-model="newAction.name"
            :label="t('name') + ' *'"
            lazy-rules
            :rules="[(val) => !!val || t('field_required')]"
          />
          <q-select
            filled
            dense
            v-model="newAction.group"
            :label="t('group') + ' *'"
            :options="actionGroupOptions"
            class="on-right"
            :rules="[(val) => !!val || t('field_required')]"
            style="min-width: 200px"
          />
          <q-btn
            icon="add"
            size="sm"
            color="primary"
            :disable="newAction.name === '' || newAction.group === ''"
            @click="actions.push(JSON.parse(JSON.stringify(newAction)))"
            class="on-right q-mb-md"
          />
        </q-toolbar>
      </q-card-section>

      <q-separator />

      <q-card-actions align="right" class="bg-grey-3">
        <q-btn flat :label="t('cancel')" color="secondary" @click="onCancel" v-close-popup />
        <q-btn flat :label="t('save')" color="primary" @click="onSave" v-close-popup />
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

const props = defineProps<DialogProps>()
const emit = defineEmits(['update:modelValue', 'saved', 'cancel'])

const showDialog = ref(props.modelValue)

const actions = ref<CompanyAction[]>([])

const newAction = ref<CompanyAction>({
  name: '',
  group: '',
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
          actions.value = JSON.parse(JSON.stringify(actionsStore.items))
        })
        .catch(notifyError)
    }
  },
)

function onHide() {
  emit('update:modelValue', false)
}

function onCancel() {
  emit('cancel', true)
}

function onSave() {
  emit('saved', true)
}

function onDeleteAction(idx: number) {
  actions.value.splice(idx, 1)
}
</script>
