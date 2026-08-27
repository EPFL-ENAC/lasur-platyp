<template>
  <div class="q-mt-lg">
    <div class="text-subtitle1">
      {{ t('lookup_address_or_select_on_map') }}
    </div>

    <div class="input-row q-mb-sm">
      <q-input
        class="address-field"
        :model-value="model?.address || ''"
        type="text"
        color="field"
        bg-color="field"
        outlined
        rounded
        dense
        :placeholder="t('type_enter_to_lookup_address')"
        :loading="loading"
        lazy-rules
        style="min-width: 250px"
        :readonly="props.readonly"
        @update:model-value="onAddressInput"
        @keyup.enter="onSuggestAddress"
      >
        <q-menu v-model="showSuggestions" no-parent-event no-focus auto-close>
          <q-list style="min-width: 100px">
            <q-item
              v-for="sugg in suggestions"
              :key="sugg.value"
              clickable
              v-close-popup
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
      </q-input>

      <q-btn
        v-if="hasLocation && !props.readonly"
        size="sm"
        color="primary"
        icon="delete"
        :title="formatCoordinates(model?.lat, model?.lon)"
        class="q-mt-xs"
        @click="onRemoveLocation"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Feature, Point } from 'geojson'
import type { AddressLocation } from '@/models'
import { geocoderApi, toAddress } from '@/utils/geocoder'
import { formatCoordinates } from '@/utils/numbers'

const { t } = useI18n()

interface Suggestion {
  value: string
  feature: Feature
}

const emit = defineEmits<{
  selected: []
  removed: []
}>()

const model = defineModel<AddressLocation | undefined>({
  required: true,
})

const props = withDefaults(
  defineProps<{
    readonly?: boolean
  }>(),
  {
    readonly: false,
  },
)

const suggestions = ref<Suggestion[]>([])
const showSuggestions = ref(false)
const loading = ref(false)

const hasLocation = computed(() => {
  if (!model.value) {
    return false
  }
  return model.value.lat != null && model.value.lon != null
})

function updateModel(patch: Partial<AddressLocation>) {
  if (!model.value) {
    model.value = {
      address: '',
      ...patch,
    }
  } else {
    model.value = {
      ...model.value,
      ...patch,
    }
  }
}

function onAddressInput(value: string | number | null) {
  updateModel({
    address: String(value ?? ''),
  })
}

function onSuggestAddress() {
  if (!model.value || !model.value.address || model.value.address.length < 3) {
    return
  }

  loading.value = true
  showSuggestions.value = false
  suggestions.value = []

  geocoderApi
    .forwardGeocode({
      query: model.value.address,
      limit: 10,
    })
    .then((collection) => {
      if (collection?.features?.length) {
        suggestions.value = collection.features
          .filter((feature) => feature.properties?.address)
          .map((feature) => ({
            value: toAddress(feature),
            feature,
          }))
      }
    })
    .catch((error) => {
      console.error(error)
    })
    .finally(() => {
      showSuggestions.value = true
      loading.value = false
    })
}

function onSuggestionSelected(suggestion: Suggestion) {
  const point = suggestion.feature.geometry as Point

  updateModel({
    address: suggestion.value,
    lat: point.coordinates[1],
    lon: point.coordinates[0],
  })

  showSuggestions.value = false
  emit('selected')
}

function onRemoveLocation() {
  updateModel({
    address: '',
    lat: undefined,
    lon: undefined,
  })

  emit('removed')
}
</script>

<style scoped>
.input-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.address-field {
  flex: 1;
}
</style>
