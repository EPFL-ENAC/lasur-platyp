<template>
  <q-dialog v-model="showDialog" persistent @hide="onHide">
    <q-card class="dialog-sm">
      <q-card-actions>
        <div class="text-h6 q-ml-sm">{{ t(editMode ? 'edit' : 'add') }}</div>
        <q-space />
        <q-btn flat icon="close" color="primary" v-close-popup />
      </q-card-actions>
      <q-separator />

      <q-card-section>
        <q-form ref="form">
          <q-input
            filled
            v-model="selected.name"
            :label="t('name') + ' *'"
            lazy-rules
            :rules="[(val) => !!val || t('field_required')]"
            class="q-mb-md"
          />
          <q-input
            v-if="editMode"
            filled
            v-model="selected.slug"
            :label="t('slug') + ' *'"
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
          <address-input
            v-model="addressLocation"
            :label="t('address') + ' *'"
            :hint="t('address_input_hint')"
            required
            class="q-mb-md"
          />
          <q-input filled v-model="selected.start_date" :label="t('start_date')" class="q-mb-md">
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
import type { Campaign, Company } from 'src/models'
import { notifyError } from 'src/utils/notify'
import AddressInput from 'src/components/AddressInput.vue'
import type { AddressLocation } from 'src/components/models'
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
const editMode = ref(false)
const addressLocation = ref<AddressLocation>({ address: '' })

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
  addressLocation.value = {
    address: selected.value.address || '',
    lat: selected.value.lat,
    lon: selected.value.lon,
  }
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
  selected.value.address = addressLocation.value.address
  selected.value.lat = addressLocation.value.lat
  selected.value.lon = addressLocation.value.lon
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
</script>
