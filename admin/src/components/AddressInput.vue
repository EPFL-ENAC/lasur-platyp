<template>
  <div>
    <q-input
      filled
      v-model="addressLocation.address"
      :label="label"
      :hint="hint"
      debounce="300"
      @keyup.enter="onSuggestAddress"
      @update:model-value="onUpdate"
      :loading="loading"
      lazy-rules
      :rules="required ? [(val) => !!val || t('field_required'), locationValidator] : []"
    >
      <q-menu v-model="showSuggestions" no-parent-event no-focus auto-close>
        <q-list style="min-width: 100px">
          <q-item
            clickable
            v-close-popup
            v-for="sugg in suggestions"
            :key="sugg.value"
            @click="onSuggestionSelected(sugg)"
          >
            <q-item-section>{{ sugg.value }}</q-item-section>
          </q-item>
          <q-item v-if="suggestions.length === 0">
            <q-item-section class="text-grey">
              {{ t('no_results') }}
            </q-item-section>
          </q-item>
        </q-list>
      </q-menu>
      <template v-slot:append>
        <q-btn round dense flat icon="search" @click="onSuggestAddress" />
      </template>
    </q-input>
    <div v-if="addressLocation.lat && addressLocation.lon" class="q-pl-sm q-mt-sm text-hint">
      <a
        :href="`https://www.google.com/maps/search/?api=1&query=${addressLocation.lat},${addressLocation.lon}`"
        target="_blank"
      >
        <q-icon name="location_on" color="grey-10" />
        {{ formatCoordinates(addressLocation.lat, addressLocation.lon) }}
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { geocoderApi, toAddress } from 'src/utils/geocoder'
import type { Feature, Point } from 'geojson'
import type { AddressLocation } from 'src/components/models'
import { formatCoordinates } from 'src/utils/numbers'

const { t } = useI18n()

interface Props {
  modelValue: AddressLocation | undefined
  label?: string
  hint?: string
  required?: boolean
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue', 'feature'])

interface Suggestion {
  value: string
  feature: Feature
}

const addressLocation = ref<AddressLocation>(props.modelValue || { address: '' })
const suggestions = ref<Suggestion[]>([])
const showSuggestions = ref(false)
const loading = ref(false)

onMounted(onInit)

watch(() => props.modelValue, onInit)

function onInit() {
  addressLocation.value = props.modelValue || { address: '' }
  suggestions.value = []
}

function onUpdate() {
  emit('update:modelValue', addressLocation.value)
}

function onSuggestAddress() {
  if (addressLocation.value?.address === undefined || addressLocation.value.address.length < 3) {
    return
  }
  loading.value = true
  showSuggestions.value = false
  geocoderApi
    .forwardGeocode({ query: addressLocation.value.address, limit: 5 })
    .then((collection) => {
      if (collection && collection.features && collection.features.length) {
        suggestions.value = collection.features
          .filter((feature) => feature.properties?.address)
          .map((feature) => ({ value: toAddress(feature), feature }))
      }
    })
    .finally(() => {
      showSuggestions.value = true
      loading.value = false
    })
}

function onSuggestionSelected(suggestion: Suggestion) {
  addressLocation.value.address = suggestion.value
  showSuggestions.value = false

  addressLocation.value.lat = (suggestion.feature.geometry as Point).coordinates[1]
  addressLocation.value.lon = (suggestion.feature.geometry as Point).coordinates[0]

  emit('feature', suggestion.feature)
  onUpdate()
}

function locationValidator() {
  return (
    (addressLocation.value.lat !== undefined &&
      addressLocation.value.lat !== null &&
      addressLocation.value.lat !== 0 &&
      addressLocation.value.lon !== undefined &&
      addressLocation.value.lon !== null &&
      addressLocation.value.lon !== 0) ||
    t('location_required')
  )
}
</script>
