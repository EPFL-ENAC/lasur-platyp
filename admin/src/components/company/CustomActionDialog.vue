<template>
  <q-dialog v-model="showDialog" persistent @hide="onHide">
    <q-card class="dialog-sm">
      <q-card-section>
        <div class="text-h6">{{ t('actions.add_custom_title') }}</div>
        <div class="text-hint">{{ t(`actions.${group}_label`) }}</div>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <q-form ref="form">
          <q-input
            outlined
            rounded
            color="field"
            v-model="labelFr"
            :label="t('label_fr') + ' *'"
            lazy-rules
            :rules="[(val) => !!val || t('field_required')]"
            autofocus
          />
          <q-input
            outlined
            rounded
            color="field"
            v-model="labelEn"
            :label="t('label_en') + ' *'"
            lazy-rules
            :rules="[(val) => !!val || t('field_required')]"
          />
        </q-form>
      </q-card-section>

      <q-separator />

      <q-card-actions align="right">
        <q-btn outline :label="t('cancel')" color="field" v-close-popup />
        <q-btn :label="t('add')" color="primary" :loading="saving" @click="onSave" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import type { Company, CompanyAction } from '@/models'
import { notifyError } from '@/utils/notify'

const { t } = useI18n()
const actionsStore = useActions()

interface DialogProps {
  modelValue: boolean
  company: Company
  group: string
}

const props = defineProps<DialogProps>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  saved: [action: CompanyAction]
}>()

const showDialog = ref(props.modelValue)
const form = ref()
const labelEn = ref('')
const labelFr = ref('')
const saving = ref(false)

watch(
  () => props.modelValue,
  (value) => {
    showDialog.value = value
    if (value) {
      labelEn.value = ''
      labelFr.value = ''
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
  saving.value = true
  actionsStore.service
    .create({
      group: props.group,
      labels: {
        en: labelEn.value,
        fr: labelFr.value,
      },
      company_id: props.company.id,
    } as CompanyAction)
    .then((res) => {
      emit('saved', res.data as CompanyAction)
      onHide()
    })
    .catch(notifyError)
    .finally(() => {
      saving.value = false
    })
}
</script>
