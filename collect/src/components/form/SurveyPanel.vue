<template>
  <div v-if="survey.record" v-touch-swipe.mouse.left.right="handleSwipe">
    <div v-if="survey.step === 1">
      <ChoiceItem
        :label="t('form.age_class')"
        :options="ageOptions"
        v-model="survey.record.data.age_class"
        :option-label-class="q.screen.lt.sm ? 'text-h5' : ''"
      />
    </div>
    <div v-if="survey.step === 2">
      <NumberItem
        :label="t('form.employment_rate')"
        v-model="survey.record.data.employment_rate"
        :min="0"
        :max="100"
        :step="5"
        unit="%"
        class="q-mb-lg"
      />
      <NumberItem
        :label="t('form.remote_work_rate')"
        v-model="survey.record.data.remote_work_rate"
        :min="0"
        :max="100"
        :step="5"
        unit="%"
        class="q-mb-lg"
      />
      <ToggleItem
        :label="t('form.company_vehicle')"
        :left-label="t('form.no')"
        :right-label="t('form.yes')"
        v-model="survey.record.data.company_vehicle"
        class="q-mb-lg"
      />
    </div>
    <div v-if="survey.step === 3">
      <LocationItem
        :label="t('form.workplace')"
        v-model="survey.record.data.workplace"
        class="q-mb-xl"
      />
      <LocationItem
        :label="t('form.origin')"
        :hint="t('form.origin_hint')"
        v-model="survey.record.data.origin"
      />
    </div>
    <div v-if="survey.step === 4">
      <NumberItem
        :label="t('form.travel_time')"
        v-model="survey.record.data.travel_time"
        :min="0"
        :max="120"
        :step="5"
        :unit-hint="t('form.travel_time_minutes')"
      />
    </div>
    <div v-if="survey.step === 5">
      <ChoiceItem
        :label="t('form.constraints')"
        :options="constraintsOptions"
        v-model="survey.record.data.constraints"
        multiple
        :option-label-class="q.screen.lt.sm ? 'text-h5' : ''"
      />
    </div>
    <div v-if="survey.step === 6">
      <ChoiceItem
        :label="t('form.equipments')"
        :options="equipmentsOptions"
        v-model="survey.record.data.equipments"
        multiple
        :option-label-class="q.screen.lt.sm ? 'text-h5' : ''"
      />
    </div>
    <div v-if="survey.step === 7">
      <SectionItem :label="t('form.freq_mod')" :hint="t('form.freq_mod_hint')" class="q-mb-lg" />
      <SliderItem
        :label="t('form.mode.walking')"
        v-model="survey.record.data.freq_mod_walking"
        :min="0"
        :max="7"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <SliderItem
        :label="t('form.mode.bike')"
        v-model="survey.record.data.freq_mod_bike"
        :min="0"
        :max="7"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <SliderItem
        :label="t('form.mode.pub')"
        v-model="survey.record.data.freq_mod_pub"
        :min="0"
        :max="7"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <SliderItem
        :label="t('form.mode.moto')"
        v-model="survey.record.data.freq_mod_moto"
        :min="0"
        :max="7"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <SliderItem
        :label="t('form.mode.car')"
        v-model="survey.record.data.freq_mod_car"
        :min="0"
        :max="7"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <SliderItem
        :label="t('form.mode.train')"
        v-model="survey.record.data.freq_mod_train"
        :min="0"
        :max="7"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <ToggleItem
        :label="t('form.mode.combined')"
        :left-label="t('form.no')"
        :right-label="t('form.yes')"
        v-model="survey.record.data.freq_mod_combined"
        class="q-mt-xl q-mb-lg"
      />
    </div>
    <div v-if="survey.step === 8">
      <NumberItem
        :label="t('form.freq_trav_pro_local')"
        :hint="t('form.freq_trav_pro_local_hint')"
        v-model="survey.record.data.freq_trav_pro_local"
        :min="0"
        :max="30"
        :step="1"
        :step2="5"
        :unit-hint="t('form.days_per_month')"
        class="q-mb-lg"
      />
    </div>
    <div v-if="survey.step === 9">
      <SectionItem
        :label="t('form.freq_mod_pro')"
        :hint="t('form.freq_trav_pro_local_hint')"
        class="q-mb-lg"
      />
      <NumberItem
        :label="t('form.mode.walking')"
        v-model="survey.record.data.freq_mod_pro_local_walking"
        :min="0"
        :max="30"
        :step="1"
        :step2="5"
        :unit-hint="t('form.days_per_month')"
        label-class="text-h5 q-pt-lg"
        class="q-mb-lg"
      />
      <NumberItem
        :label="t('form.mode.bike')"
        v-model="survey.record.data.freq_mod_pro_local_bike"
        :min="0"
        :max="30"
        :step="1"
        :step2="5"
        :unit-hint="t('form.days_per_month')"
        label-class="text-h5 q-pt-lg"
        class="q-mb-lg"
      />
      <NumberItem
        :label="t('form.mode.pub')"
        v-model="survey.record.data.freq_mod_pro_local_pub"
        :min="0"
        :max="30"
        :step="1"
        :step2="5"
        :unit-hint="t('form.days_per_month')"
        label-class="text-h5 q-pt-lg"
        class="q-mb-lg"
      />
      <NumberItem
        :label="t('form.mode.moto')"
        v-model="survey.record.data.freq_mod_pro_local_moto"
        :min="0"
        :max="30"
        :step="1"
        :step2="5"
        :unit-hint="t('form.days_per_month')"
        label-class="text-h5 q-pt-lg"
        class="q-mb-lg"
      />
      <NumberItem
        :label="t('form.mode.car')"
        v-model="survey.record.data.freq_mod_pro_local_car"
        :min="0"
        :max="30"
        :step="1"
        :step2="5"
        :unit-hint="t('form.days_per_month')"
        label-class="text-h5 q-pt-lg"
        class="q-mb-lg"
      />
      <NumberItem
        :label="t('form.mode.train')"
        v-model="survey.record.data.freq_mod_pro_local_train"
        :min="0"
        :max="30"
        :step="1"
        :step2="5"
        :unit-hint="t('form.days_per_month')"
        label-class="text-h5 q-pt-lg"
        class="q-mb-lg"
      />
      <ToggleItem
        :label="t('form.mode.combined')"
        :left-label="t('form.no')"
        :right-label="t('form.yes')"
        v-model="survey.record.data.freq_mod_pro_local_combined"
        class="q-mt-xl q-mb-lg"
      />
    </div>
    <div v-if="survey.step === 10">
      <NumberItem
        :label="t('form.freq_trav_pro_region')"
        :hint="t('form.freq_trav_pro_region_hint')"
        v-model="survey.record.data.freq_trav_pro_region"
        :min="0"
        :max="30"
        :step="1"
        :step2="5"
        :unit-hint="t('form.days_per_month')"
        class="q-mb-lg"
      />
    </div>
    <div v-if="survey.step === 11">
      <SectionItem
        :label="t('form.freq_mod_pro')"
        :hint="t('form.freq_trav_pro_region_hint')"
        class="q-mb-lg"
      />
      <NumberItem
        :label="t('form.mode.pub')"
        v-model="survey.record.data.freq_mod_pro_region_pub"
        :min="0"
        :max="30"
        :step="1"
        :step2="5"
        :unit-hint="t('form.days_per_month')"
        label-class="text-h5 q-pt-lg"
        class="q-mb-lg"
      />
      <NumberItem
        :label="t('form.mode.moto')"
        v-model="survey.record.data.freq_mod_pro_region_moto"
        :min="0"
        :max="30"
        :step="1"
        :step2="5"
        :unit-hint="t('form.days_per_month')"
        label-class="text-h5 q-pt-lg"
        class="q-mb-lg"
      />
      <NumberItem
        :label="t('form.mode.car')"
        v-model="survey.record.data.freq_mod_pro_region_car"
        :min="0"
        :max="30"
        :step="1"
        :step2="5"
        :unit-hint="t('form.days_per_month')"
        label-class="text-h5 q-pt-lg"
        class="q-mb-lg"
      />
      <NumberItem
        :label="t('form.mode.train')"
        v-model="survey.record.data.freq_mod_pro_region_train"
        :min="0"
        :max="30"
        :step="1"
        :step2="5"
        :unit-hint="t('form.days_per_month')"
        label-class="text-h5 q-pt-lg"
        class="q-mb-lg"
      />
      <NumberItem
        :label="t('form.mode.plane')"
        v-model="survey.record.data.freq_mod_pro_region_plane"
        :min="0"
        :max="30"
        :step="1"
        :step2="5"
        :unit-hint="t('form.days_per_month')"
        label-class="text-h5 q-pt-lg"
        class="q-mb-lg"
      />
      <ToggleItem
        :label="t('form.mode.combined')"
        :left-label="t('form.no')"
        :right-label="t('form.yes')"
        v-model="survey.record.data.freq_mod_pro_region_combined"
        class="q-mt-xl q-mb-lg"
      />
    </div>
    <div v-if="survey.step === 12">
      <NumberItem
        :label="t('form.freq_trav_pro_inter')"
        :hint="t('form.freq_trav_pro_inter_hint')"
        v-model="survey.record.data.freq_trav_pro_inter"
        :min="0"
        :max="30"
        :step="1"
        :step2="5"
        :unit-hint="t('form.days_per_month')"
        class="q-mb-lg"
      />
    </div>
    <div v-if="survey.step === 13">
      <SectionItem
        :label="t('form.freq_mod_pro')"
        :hint="t('form.freq_trav_pro_inter_hint')"
        class="q-mb-lg"
      />
      <NumberItem
        :label="t('form.mode.car')"
        v-model="survey.record.data.freq_mod_pro_inter_car"
        :min="0"
        :max="30"
        :step="1"
        :step2="5"
        :unit-hint="t('form.days_per_month')"
        label-class="text-h5 q-pt-lg"
        class="q-mb-lg"
      />
      <NumberItem
        :label="t('form.mode.train')"
        v-model="survey.record.data.freq_mod_pro_inter_train"
        :min="0"
        :max="30"
        :step="1"
        :step2="5"
        :unit-hint="t('form.days_per_month')"
        label-class="text-h5 q-pt-lg"
        class="q-mb-lg"
      />
      <NumberItem
        :label="t('form.mode.plane')"
        v-model="survey.record.data.freq_mod_pro_inter_plane"
        :min="0"
        :max="30"
        :step="1"
        :step2="5"
        :unit-hint="t('form.days_per_month')"
        label-class="text-h5 q-pt-lg"
        class="q-mb-lg"
      />
      <ToggleItem
        :label="t('form.mode.combined')"
        :left-label="t('form.no')"
        :right-label="t('form.yes')"
        v-model="survey.record.data.freq_mod_pro_inter_combined"
        class="q-mt-xl q-mb-lg"
      />
    </div>
    <div v-if="survey.step === 14">
      <SectionItem
        :label="t('form.importance')"
        :hint="t('form.importance_hint')"
        class="q-mb-lg"
      />
      <RatingItem
        :label="t('form.importance_time')"
        v-model="survey.record.data.importance_time"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <RatingItem
        :label="t('form.importance_cost')"
        v-model="survey.record.data.importance_cost"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <RatingItem
        :label="t('form.importance_flex')"
        v-model="survey.record.data.importance_flex"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <RatingItem
        :label="t('form.importance_rel')"
        v-model="survey.record.data.importance_rel"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <RatingItem
        :label="t('form.importance_comfort')"
        v-model="survey.record.data.importance_comfort"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <RatingItem
        :label="t('form.importance_most')"
        v-model="survey.record.data.importance_most"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <RatingItem
        :label="t('form.importance_env')"
        v-model="survey.record.data.importance_env"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
    </div>
    <div v-if="survey.step === 15">
      <SectionItem :label="t('form.needs')" :hint="t('form.needs_hint')" class="q-mb-lg" />
      <RatingItem
        :label="t('form.mode.walking')"
        v-model="survey.record.data.needs_walking"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <RatingItem
        :label="t('form.mode.bike')"
        v-model="survey.record.data.needs_bike"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <RatingItem
        :label="t('form.mode.pub')"
        v-model="survey.record.data.needs_pub"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <RatingItem
        :label="t('form.mode.moto')"
        v-model="survey.record.data.needs_moto"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <RatingItem
        :label="t('form.mode.car')"
        v-model="survey.record.data.needs_car"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <RatingItem
        :label="t('form.mode.train')"
        v-model="survey.record.data.needs_train"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
    </div>
    <div v-if="survey.step === 16">
      <SectionItem
        :label="t('form.adjectives')"
        :hint="t('form.adjectives_hint')"
        class="q-mb-lg"
      />
      <ToggleChoiceItem
        :label="t('form.mode.bike')"
        :options="adjectivePairsOptions"
        v-model="survey.record.data.adjectives_bikes"
        :max="3"
        :col="q.screen.lt.sm ? 1 : 2"
        option-label-class="text-h6"
        class="q-mb-lg"
      />
    </div>
    <div v-if="survey.step === 17">
      <SectionItem
        :label="t('form.adjectives')"
        :hint="t('form.adjectives_hint')"
        class="q-mb-lg"
      />
      <ToggleChoiceItem
        :label="t('form.mode.pub_train')"
        :options="adjectivePairsOptions"
        v-model="survey.record.data.adjectives_pubs"
        :max="3"
        :col="q.screen.lt.sm ? 1 : 2"
        option-label-class="text-h6"
        class="q-mb-lg"
      />
    </div>
    <div v-if="survey.step === 18">
      <SectionItem
        :label="t('form.adjectives')"
        :hint="t('form.adjectives_hint')"
        class="q-mb-lg"
      />
      <ToggleChoiceItem
        :label="t('form.mode.car_moto')"
        :options="adjectivePairsOptions"
        v-model="survey.record.data.adjectives_motors"
        :max="3"
        :col="q.screen.lt.sm ? 1 : 2"
        option-label-class="text-h6"
        class="q-mb-lg"
      />
    </div>
    <div v-if="survey.step === 19">
      <RecommendationsPanel />
      <RecommendationsProPanel class="q-mt-xl" />
      <q-btn
        outlined
        no-caps
        color="primary"
        :icon-right="showDebug ? 'keyboard_arrow_up' : 'keyboard_arrow_down'"
        size="sm"
        label="Debug"
        @click="showDebug = !showDebug"
        class="q-mt-md"
      />
      <div v-if="showDebug">
        <pre>{{ survey.recommendation }}</pre>
        <pre>{{ survey.record }}</pre>
      </div>
    </div>
    <div v-if="survey.step === 20">
      <SectionItem :label="t('form.comments')" class="q-mb-lg" />
      <q-input
        v-model="survey.record.data.comments"
        type="textarea"
        class="q-mb-lg text-h4"
        bg-color="green-3"
        filled
      />
    </div>
    <div class="row justify-center q-mt-xl">
      <q-btn
        rounded
        v-if="survey.step > 1"
        color="accent"
        icon="keyboard_arrow_left"
        size="lg"
        @click="prevStep"
        class="q-mr-md"
      />
      <q-btn
        rounded
        v-if="survey.step < 20"
        color="accent"
        icon="keyboard_arrow_right"
        size="lg"
        @click="nextStep"
        class="q-ml-md"
      />
      <q-btn
        rounded
        v-if="survey.step === 20"
        color="primary"
        :label="t('send')"
        icon-right="send"
        size="lg"
        class="q-ml-md"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar'
import type { Option, ToggleOption } from 'src/components/form/models'
import ChoiceItem from 'src/components/form/ChoiceItem.vue'
import ToggleChoiceItem from 'src/components/form/ToggleChoiceItem.vue'
import NumberItem from 'src/components/form/NumberItem.vue'
import ToggleItem from 'src/components/form/ToggleItem.vue'
import SectionItem from 'src/components/form/SectionItem.vue'
import SliderItem from 'src/components/form/SliderItem.vue'
import RatingItem from 'src/components/form/RatingItem.vue'
import LocationItem from 'src/components/form/LocationItem.vue'
import RecommendationsPanel from 'src/components/form/RecommendationsPanel.vue'
import RecommendationsProPanel from 'src/components/form/RecommendationsProPanel.vue'
import { notifyError } from 'src/utils/notify'

const { t } = useI18n()
const survey = useSurvey()
const collector = useCollector()
const q = useQuasar()

watch(
  () => survey.record,
  () => {
    console.debug(survey.record.data)
  },
  { deep: true },
)

const showDebug = ref(false)

const ageOptions = computed<Option[]>(() => [
  { value: '16-17', label: t('form.age_class_option.16_17') },
  { value: '18-24', label: t('form.age_class_option.18_24') },
  { value: '26-44', label: t('form.age_class_option.25_44') },
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

const adjectivePairsOptions = computed<ToggleOption[]>(() => [
  {
    trueValue: 'fast',
    trueLabel: t('form.adjectives_option.fast'),
    falseValue: 'slow',
    falseLabel: t('form.adjectives_option.slow'),
  },
  {
    trueValue: 'cheap',
    trueLabel: t('form.adjectives_option.cheap'),
    falseValue: 'expensive',
    falseLabel: t('form.adjectives_option.expensive'),
  },
  {
    trueValue: 'practical',
    trueLabel: t('form.adjectives_option.practical'),
    falseValue: 'impractical',
    falseLabel: t('form.adjectives_option.impractical'),
  },
  {
    trueValue: 'ecological',
    trueLabel: t('form.adjectives_option.ecological'),
    falseValue: 'polluting',
    falseLabel: t('form.adjectives_option.polluting'),
  },
  {
    trueValue: 'safe',
    trueLabel: t('form.adjectives_option.safe'),
    falseValue: 'dangerous',
    falseLabel: t('form.adjectives_option.dangerous'),
  },
  {
    trueValue: 'pleasant',
    trueLabel: t('form.adjectives_option.pleasant'),
    falseValue: 'unpleasant',
    falseLabel: t('form.adjectives_option.unpleasant'),
  },
  {
    trueValue: 'autonomous',
    trueLabel: t('form.adjectives_option.autonomous'),
    falseValue: 'constraining',
    falseLabel: t('form.adjectives_option.constraining'),
  },
  {
    trueValue: 'relax',
    trueLabel: t('form.adjectives_option.relax'),
    falseValue: 'tiring',
    falseLabel: t('form.adjectives_option.tiring'),
  },
  {
    trueValue: 'healthy',
    trueLabel: t('form.adjectives_option.healthy'),
    falseValue: 'bad_weather',
    falseLabel: t('form.adjectives_option.bad_weather'),
  },
  {
    trueValue: 'reliable',
    trueLabel: t('form.adjectives_option.reliable'),
    falseValue: 'congested',
    falseLabel: t('form.adjectives_option.congested'),
  },
])

function nextStep() {
  if (survey.step === 20) return
  if (survey.step === 3) {
    if (
      survey.record.data.workplace?.lat === undefined ||
      survey.record.data.workplace?.lat === 0
    ) {
      notifyError(t('form.error.workplace'))
      return
    }
    if (survey.record.data.origin?.lat === undefined || survey.record.data.origin?.lat === 0) {
      notifyError(t('form.error.origin'))
      return
    }
  }
  survey.incStep()
  if (survey.tokenOrSlug) {
    if (survey.step === 19) {
      survey.recommendation = {}
      collector
        .save(survey.tokenOrSlug, survey.record)
        .then(() => {
          return collector.loadTypo(survey.record)
        })
        .then((resp) => {
          console.log(resp)
          survey.recommendation = resp
        })
        .catch(notifyError)
    } else {
      void collector.save(survey.tokenOrSlug, survey.record).catch(console.error)
    }
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function prevStep() {
  if (survey.step === 1) return
  survey.decStep()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function handleSwipe(dir: any) {
  if (dir['direction'] === 'left') {
    nextStep()
  } else if (dir['direction'] === 'right') {
    prevStep()
  }
}
</script>
