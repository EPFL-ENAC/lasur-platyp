<template>
  <div v-if="collector.caseReport">
    <ChoiceItem
      :label="t('form.age_class')"
      :options="ageOptions"
      v-model="collector.caseReport.data.age_class"
      :option-label-class="q.screen.lt.sm ? 'text-h5' : ''"
    />
    <q-separator dark class="q-mt-xl q-mb-xl" />
    <NumberItem
      :label="t('form.employment_rate')"
      v-model="collector.caseReport.data.employment_rate"
      :min="0"
      :max="100"
      :step="5"
      unit="%"
    />
    <q-separator dark class="q-mt-xl q-mb-xl" />
    <NumberItem
      :label="t('form.remote_work_rate')"
      v-model="collector.caseReport.data.remote_work_rate"
      :min="0"
      :max="100"
      :step="5"
      unit="%"
    />
    <q-separator dark class="q-mt-xl q-mb-xl" />
    <ToggleItem
      :label="t('form.company_vehicle')"
      :left-label="t('form.no')"
      :right-label="t('form.yes')"
      v-model="collector.caseReport.data.company_vehicle"
    />
    <q-separator dark class="q-mt-xl q-mb-xl" />
    <NumberItem
      :label="t('form.travel_time')"
      v-model="collector.caseReport.data.travel_time"
      :min="0"
      :max="120"
      :step="5"
      :unit-hint="t('form.travel_time_minutes')"
    />
    <q-separator dark class="q-mt-xl q-mb-xl" />
    <ChoiceItem
      :label="t('form.constraints')"
      :options="constraintsOptions"
      v-model="collector.caseReport.data.constraints"
      multiple
      :option-label-class="q.screen.lt.sm ? 'text-h5' : ''"
    />
    <q-separator dark class="q-mt-xl q-mb-xl" />
    <ChoiceItem
      :label="t('form.equipments')"
      :options="equipmentsOptions"
      v-model="collector.caseReport.data.equipments"
      multiple
      :option-label-class="q.screen.lt.sm ? 'text-h5' : ''"
    />
    <q-separator dark class="q-mt-xl q-mb-xl" />
    <SectionItem :label="t('form.freq_mod')" :hint="t('form.freq_mod_hint')" class="q-mb-lg" />
    <SliderItem
      :label="t('form.mode.walking')"
      v-model="collector.caseReport.data.freq_mod_walking"
      :min="0"
      :max="7"
      class="q-mb-lg"
    />
    <SliderItem
      :label="t('form.mode.bike')"
      v-model="collector.caseReport.data.freq_mod_bike"
      :min="0"
      :max="7"
      class="q-mb-lg"
    />
    <SliderItem
      :label="t('form.mode.pub')"
      v-model="collector.caseReport.data.freq_mod_pub"
      :min="0"
      :max="7"
      class="q-mb-lg"
    />
    <SliderItem
      :label="t('form.mode.moto')"
      v-model="collector.caseReport.data.freq_mod_moto"
      :min="0"
      :max="7"
      class="q-mb-lg"
    />
    <SliderItem
      :label="t('form.mode.car')"
      v-model="collector.caseReport.data.freq_mod_car"
      :min="0"
      :max="7"
      class="q-mb-lg"
    />
    <SliderItem
      :label="t('form.mode.train')"
      v-model="collector.caseReport.data.freq_mod_train"
      :min="0"
      :max="7"
      class="q-mb-lg"
    />
    <q-separator dark class="q-mt-xl q-mb-xl" />
    <SectionItem :label="t('form.freq_trav_pro')" class="q-mb-lg" />
    <NumberItem
      :label="t('form.freq_trav_pro_local')"
      v-model="collector.caseReport.data.freq_trav_pro_local"
      :min="0"
      :max="365"
      :step="1"
      :step2="5"
      :unit-hint="t('form.days_per_year')"
      label-class="text-h5 q-pt-lg"
      class="q-mb-lg"
    />
    <NumberItem
      :label="t('form.freq_trav_pro_region')"
      v-model="collector.caseReport.data.freq_trav_pro_region"
      :min="0"
      :max="365"
      :step="1"
      :step2="5"
      :unit-hint="t('form.days_per_year')"
      label-class="text-h5 q-pt-lg"
      class="q-mb-lg"
    />
    <NumberItem
      :label="t('form.freq_trav_pro_inter')"
      v-model="collector.caseReport.data.freq_trav_pro_inter"
      :min="0"
      :max="365"
      :step="1"
      :step2="5"
      :unit-hint="t('form.days_per_year')"
      label-class="text-h5 q-pt-lg"
      class="q-mb-lg"
    />
    <q-separator dark class="q-mt-xl q-mb-xl" />
    <SectionItem :label="t('form.freq_mod_pro')" class="q-mb-lg" />
    <NumberItem
      :label="t('form.mode.walking')"
      v-model="collector.caseReport.data.freq_mod_pro_walking"
      :min="0"
      :max="365"
      :step="1"
      :step2="5"
      :unit-hint="t('form.days_per_year')"
      label-class="text-h5 q-pt-lg"
      class="q-mb-lg"
    />
    <NumberItem
      :label="t('form.mode.bike')"
      v-model="collector.caseReport.data.freq_mod_pro_bike"
      :min="0"
      :max="365"
      :step="1"
      :step2="5"
      :unit-hint="t('form.days_per_year')"
      label-class="text-h5 q-pt-lg"
      class="q-mb-lg"
    />
    <NumberItem
      :label="t('form.mode.pub')"
      v-model="collector.caseReport.data.freq_mod_pro_pub"
      :min="0"
      :max="365"
      :step="1"
      :step2="5"
      :unit-hint="t('form.days_per_year')"
      label-class="text-h5 q-pt-lg"
      class="q-mb-lg"
    />
    <NumberItem
      :label="t('form.mode.moto')"
      v-model="collector.caseReport.data.freq_mod_pro_moto"
      :min="0"
      :max="365"
      :step="1"
      :step2="5"
      :unit-hint="t('form.days_per_year')"
      label-class="text-h5 q-pt-lg"
      class="q-mb-lg"
    />
    <NumberItem
      :label="t('form.mode.car')"
      v-model="collector.caseReport.data.freq_mod_pro_car"
      :min="0"
      :max="365"
      :step="1"
      :step2="5"
      :unit-hint="t('form.days_per_year')"
      label-class="text-h5 q-pt-lg"
      class="q-mb-lg"
    />
    <NumberItem
      :label="t('form.mode.train')"
      v-model="collector.caseReport.data.freq_mod_pro_train"
      :min="0"
      :max="365"
      :step="1"
      :step2="5"
      :unit-hint="t('form.days_per_year')"
      label-class="text-h5 q-pt-lg"
      class="q-mb-lg"
    />
    <NumberItem
      :label="t('form.mode.plane')"
      v-model="collector.caseReport.data.freq_mod_pro_plane"
      :min="0"
      :max="365"
      :step="1"
      :step2="5"
      :unit-hint="t('form.days_per_year')"
      label-class="text-h5 q-pt-lg"
      class="q-mb-lg"
    />
    <q-separator dark class="q-mt-xl q-mb-xl" />
    <SectionItem :label="t('form.importance')" :hint="t('form.importance_hint')" class="q-mb-lg" />
    <RatingItem
      :label="t('form.importance_time')"
      v-model="collector.caseReport.data.importance_time"
      :max="5"
      class="q-mb-lg"
    />
    <RatingItem
      :label="t('form.importance_cost')"
      v-model="collector.caseReport.data.importance_cost"
      :max="5"
      class="q-mb-lg"
    />
    <RatingItem
      :label="t('form.importance_flex')"
      v-model="collector.caseReport.data.importance_flex"
      :max="5"
      class="q-mb-lg"
    />
    <RatingItem
      :label="t('form.importance_rel')"
      v-model="collector.caseReport.data.importance_rel"
      :max="5"
      class="q-mb-lg"
    />
    <RatingItem
      :label="t('form.importance_comfort')"
      v-model="collector.caseReport.data.importance_comfort"
      :max="5"
      class="q-mb-lg"
    />
    <RatingItem
      :label="t('form.importance_most')"
      v-model="collector.caseReport.data.importance_most"
      :max="5"
      class="q-mb-lg"
    />
    <RatingItem
      :label="t('form.importance_env')"
      v-model="collector.caseReport.data.importance_env"
      :max="5"
      class="q-mb-lg"
    />
    <q-separator dark class="q-mt-xl q-mb-xl" />
    <SectionItem :label="t('form.needs')" :hint="t('form.needs_hint')" class="q-mb-lg" />
    <RatingItem
      :label="t('form.mode.walking')"
      v-model="collector.caseReport.data.needs_walking"
      :max="5"
      class="q-mb-lg"
    />
    <RatingItem
      :label="t('form.mode.bike')"
      v-model="collector.caseReport.data.needs_bike"
      :max="5"
      class="q-mb-lg"
    />
    <RatingItem
      :label="t('form.mode.pub')"
      v-model="collector.caseReport.data.needs_pub"
      :max="5"
      class="q-mb-lg"
    />
    <RatingItem
      :label="t('form.mode.moto')"
      v-model="collector.caseReport.data.needs_moto"
      :max="5"
      class="q-mb-lg"
    />
    <RatingItem
      :label="t('form.mode.car')"
      v-model="collector.caseReport.data.needs_car"
      :max="5"
      class="q-mb-lg"
    />
    <RatingItem
      :label="t('form.mode.train')"
      v-model="collector.caseReport.data.needs_train"
      :max="5"
      class="q-mb-lg"
    />
    <q-separator dark class="q-mt-xl q-mb-xl" />
    <SectionItem :label="t('form.adjectives')" :hint="t('form.adjectives_hint')" class="q-mb-lg" />
    <ChoiceItem
      :label="t('form.mode.bike')"
      :options="adjectivesOptions"
      v-model="collector.caseReport.data.adjectives_bikes"
      multiple
      :max="3"
      :col="q.screen.lt.sm ? 2 : q.screen.lt.md ? 3 : 4"
      option-label-class="text-h6"
      class="q-mb-lg"
    />
    <ChoiceItem
      :label="t('form.mode.pub_train')"
      :options="adjectivesOptions"
      v-model="collector.caseReport.data.adjectives_pubs"
      multiple
      :max="3"
      :col="q.screen.lt.sm ? 2 : q.screen.lt.md ? 3 : 4"
      option-label-class="text-h6"
      class="q-mb-lg"
    />
    <ChoiceItem
      :label="t('form.mode.car_moto')"
      :options="adjectivesOptions"
      v-model="collector.caseReport.data.adjectives_motors"
      multiple
      :max="3"
      :col="q.screen.lt.sm ? 2 : q.screen.lt.md ? 3 : 4"
      option-label-class="text-h6"
      class="q-mb-lg"
    />
    <q-separator dark class="q-mt-xl q-mb-xl" />
    <pre>{{ collector.caseReport.data }}</pre>
  </div>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar'
import type { Option } from 'src/components/form/models'
import ChoiceItem from 'src/components/form/ChoiceItem.vue'
import NumberItem from 'src/components/form/NumberItem.vue'
import ToggleItem from 'src/components/form/ToggleItem.vue'
import SectionItem from 'src/components/form/SectionItem.vue'
import SliderItem from 'src/components/form/SliderItem.vue'
import RatingItem from 'src/components/form/RatingItem.vue'

const { t } = useI18n()
const collector = useCollector()
const q = useQuasar()

watch(
  () => collector.caseReport,
  () => {
    console.debug(collector.caseReport.data)
  },
  { deep: true },
)

const ageOptions = computed<Option[]>(() => [
  { value: '16-17', label: t('form.age_class_option.16_17') },
  { value: '18-24', label: t('form.age_class_option.18_24') },
  { value: '26-44', label: t('form.age_class_option.26_44') },
  { value: '45-64', label: t('form.age_class_option.45_64') },
  { value: '65+', label: t('form.age_class_option.65') },
])

const equipmentsOptions = computed<Option[]>(() => [
  { value: 'bike', label: t('form.equipments_option.bike') },
  { value: 'eab', label: t('form.equipments_option.eab') },
  { value: 'moto', label: t('form.equipments_option.moto') },
  { value: 'upt_subs', label: t('form.equipments_option.upt_subs') },
  { value: 'train_subs', label: t('form.equipments_option.train_subs') },
  { value: 'mob_subs', label: t('form.equipments_option.mob_subs') },
  { value: 'car_driver', label: t('form.equipments_option.car_driver') },
  { value: 'car_passenger', label: t('form.equipments_option.car_passenger') },
])

const constraintsOptions = computed<Option[]>(() => [
  { value: 'dependent', label: t('form.constraints_option.dependent') },
  { value: 'heavy', label: t('form.constraints_option.heavy') },
  { value: 'night', label: t('form.constraints_option.night') },
  { value: 'disabled', label: t('form.constraints_option.disabled') },
])

const adjectivesOptions = computed<Option[]>(() => [
  { value: 'fast', label: t('form.adjectives_option.fast') },
  { value: 'safe', label: t('form.adjectives_option.safe') },
  { value: 'relax', label: t('form.adjectives_option.relax') },
  { value: 'reliable', label: t('form.adjectives_option.reliable') },
  { value: 'impractical', label: t('form.adjectives_option.impractical') },
  { value: 'constraining', label: t('form.adjectives_option.constraining') },
  { value: 'theft', label: t('form.adjectives_option.theft') },
  { value: 'cheap', label: t('form.adjectives_option.cheap') },
  { value: 'pleasant', label: t('form.adjectives_option.pleasant') },
  { value: 'useful', label: t('form.adjectives_option.useful') },
  { value: 'well_served', label: t('form.adjectives_option.well_served') },
  { value: 'polluting', label: t('form.adjectives_option.polluting') },
  { value: 'noisy', label: t('form.adjectives_option.noisy') },
  { value: 'bad_weather', label: t('form.adjectives_option.bad_weather') },
  { value: 'practical', label: t('form.adjectives_option.practical') },
  { value: 'autonomous', label: t('form.adjectives_option.autonomous') },
  { value: 'indispensable', label: t('form.adjectives_option.indispensable') },
  { value: 'slow', label: t('form.adjectives_option.slow') },
  { value: 'dangerous', label: t('form.adjectives_option.dangerous') },
  { value: 'tiring', label: t('form.adjectives_option.tiring') },
  { value: 'congested', label: t('form.adjectives_option.congested') },
  { value: 'ecological', label: t('form.adjectives_option.ecological') },
  { value: 'quiet', label: t('form.adjectives_option.quiet') },
  { value: 'healthy', label: t('form.adjectives_option.healthy') },
  { value: 'expensive', label: t('form.adjectives_option.expensive') },
  { value: 'unpleasant', label: t('form.adjectives_option.unpleasant') },
  { value: 'useless', label: t('form.adjectives_option.useless') },
  { value: 'poorly_served', label: t('form.adjectives_option.poorly_served') },
])
</script>
