<template>
  <div>
    <q-input
      filled
      v-model="selected.name"
      :label="t('campaign.workplaces.name') + ' *'"
      :hint="t('campaign.workplaces.name_hint')"
      class="q-mb-md"
      lazy-rules
      :rules="[(val) => !!val || t('field_required')]"
      @update:model-value="onUpdated"
    />
    <address-input
      v-model="addressLocation"
      :label="t('address') + ' *'"
      :hint="t('address_input_hint')"
      required
      @update:model-value="onUpdated"
    />
  </div>
</template>

<script setup lang="ts">
import AddressInput from 'src/components/AddressInput.vue'
import type { AddressLocation } from 'src/components/models'
import type { Workplace } from 'src/models'

const { t } = useI18n()
interface Props {
  modelValue: Workplace
}
const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const selected = ref<Workplace>(props.modelValue)
const addressLocation = ref<AddressLocation>({ address: '' })

onMounted(() => {
  addressLocation.value = {
    address: selected.value.address,
    lat: selected.value.lat,
    lon: selected.value.lon,
  }
})

function onUpdated() {
  selected.value.address = addressLocation.value.address
  selected.value.lat = addressLocation.value.lat || 0
  selected.value.lon = addressLocation.value.lon || 0
  emit('update:modelValue', selected.value)
}
</script>
