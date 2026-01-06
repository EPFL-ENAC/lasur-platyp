<template>
  <div>
    <SelectItem
      v-if="workplaceOptions.length > 0"
      :options="workplaceOptions"
      v-model="selectedWorkplace"
      :option-label-class="'text-h6 text-bold'"
      :col="workplaceOptions.length > 1 ? 2 : 1"
      @update:modelValue="onWorkplaceSelected"
      class="q-mb-lg"
    />
    <LocationItem
      v-if="selectedWorkplace === OTHER_WORKPLACE_OPTION"
      map-id="workplace-map"
      v-model="survey.record.data.workplace"
      class="q-mb-xl"
    />
    <LocationItem
      map-id="origin-map"
      :label="t('form.origin')"
      :hint="t('form.origin_hint')"
      v-model="survey.record.data.origin"
      class="q-mt-xl"
    />
  </div>
</template>

<script setup lang="ts">
import LocationItem from 'src/components/form/LocationItem.vue'
import SelectItem from 'src/components/form/SelectItem.vue'
import type { Option } from 'src/components/form/models'

const { t } = useI18n()
const survey = useSurvey()
const collector = useCollector()

const OTHER_WORKPLACE_OPTION = '_other'

const selectedWorkplace = ref<string>(survey.record.data.workplace?.name || '')

const workplaceOptions = computed<Option[]>(() => {
  const options = (
    collector.info?.workplaces?.map((wp) => ({
      value: wp.name || '',
      label: wp.name || wp.address || '',
      hint: wp.address || '',
    })) || []
  ).sort((a, b) => a.label.localeCompare(b.label))
  if (collector.info?.open_workplaces) {
    options.push({
      value: OTHER_WORKPLACE_OPTION,
      label: t('form.workplace_option.other'),
      hint: '',
    })
  }
  return options
})

function onWorkplaceSelected() {
  if (selectedWorkplace.value === OTHER_WORKPLACE_OPTION) {
    survey.record.data.workplace = {
      lat: 0,
      lon: 0,
      address: '',
      name: OTHER_WORKPLACE_OPTION,
    }
    return
  }
  const wp = collector.info?.workplaces?.find(
    (w) => (w.name || w.address || '') === selectedWorkplace.value,
  )
  if (wp) {
    survey.record.data.workplace = {
      lat: wp.lat,
      lon: wp.lon,
      address: wp.address,
      name: wp.name,
    }
  } else {
    survey.record.data.workplace = {
      lat: 0,
      lon: 0,
      address: '',
    }
  }
}
</script>
