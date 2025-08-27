<template>
  <div v-if="survey.record" v-touch-swipe.mouse.left.right="handleSwipe">
    <!--pre>{{ survey.step }} - {{ survey.stepName }}</pre-->
    <div v-if="survey.stepName === 'agreement'">
      <SectionItem :label="t('form.agreement')" :hint="t('form.agreement_hint')" class="q-mb-lg" />
      <div class="bg-primary rounded-borders q-pa-md q-mt-lg">
        <q-checkbox
          v-model="survey.record.data.terms_conditions"
          :label="t('form.terms_conditions')"
          size="xl"
          color="green-6"
          class="text-h6"
        />
        <div class="text-h6 q-ml-xl">
          <a href="https://modus-ge.ch/toolkit-cgu" target="_blank" class="text-secondary q-ml-sm">
            {{ t('form.terms_conditions_link') }}
            <q-icon name="open_in_new" size="xs" />
          </a>
        </div>
      </div>
      <div class="bg-primary rounded-borders q-pa-md q-mt-lg">
        <q-checkbox
          v-model="survey.record.data.confidentiality"
          :label="t('form.confidentiality')"
          size="xl"
          color="green-6"
          class="text-h6"
        />
        <div class="text-h6 q-ml-xl">
          <a
            href="https://modus-ge.ch/toolkit-privacy-notice"
            target="_blank"
            class="text-secondary q-ml-sm"
          >
            {{ t('form.confidentiality_link') }}
            <q-icon name="open_in_new" size="xs"
          /></a>
        </div>
      </div>
    </div>
    <div v-if="survey.stepName === 'age_class'">
      <ChoiceItem
        :label="t('form.age_class')"
        :options="ageOptions"
        v-model="survey.record.data.age_class"
        :option-label-class="q.screen.lt.sm ? 'text-h5' : ''"
      />
    </div>
    <div v-if="survey.stepName === 'employment'">
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
    <div v-if="survey.stepName === 'places'">
      <LocationItem
        map-id="workplace-map"
        :label="t('form.workplace')"
        v-model="survey.record.data.workplace"
        class="q-mb-xl"
      />
      <LocationItem
        map-id="origin-map"
        :label="t('form.origin')"
        :hint="t('form.origin_hint')"
        v-model="survey.record.data.origin"
      />
    </div>
    <div v-if="survey.stepName === 'travel_time'">
      <NumberItem
        :label="t('form.travel_time')"
        v-model="survey.record.data.travel_time"
        :min="5"
        :max="120"
        :step="5"
        :unit-hint="t('form.travel_time_minutes')"
      />
    </div>
    <div v-if="survey.stepName === 'constraints'">
      <ChoiceItem
        :label="t('form.constraints')"
        :options="constraintsOptions"
        v-model="survey.record.data.constraints"
        multiple
        :option-label-class="q.screen.lt.sm ? 'text-h5' : ''"
      />
    </div>
    <div v-if="survey.stepName === 'equipments'">
      <ChoiceItem
        :label="t('form.equipments')"
        :options="equipmentsOptions"
        v-model="survey.record.data.equipments"
        multiple
        :option-label-class="q.screen.lt.sm ? 'text-h5' : ''"
      />
    </div>
    <div v-if="survey.stepName === 'freq_mod'">
      <SectionItem :label="t('form.freq_mod')" :hint="t('form.freq_mod_hint')" class="q-mb-lg" />
      <SliderItem
        :label="t('form.mode.walking')"
        v-model="survey.record.data.freq_mod_walking"
        :min="0"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <SliderItem
        :label="t('form.mode.bike')"
        v-model="survey.record.data.freq_mod_bike"
        :min="0"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <SliderItem
        :label="t('form.mode.pub')"
        v-model="survey.record.data.freq_mod_pub"
        :min="0"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <SliderItem
        :label="t('form.mode.train')"
        v-model="survey.record.data.freq_mod_train"
        :min="0"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <SliderItem
        :label="t('form.mode.moto')"
        v-model="survey.record.data.freq_mod_moto"
        :min="0"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
      />
      <SliderItem
        :label="t('form.mode.car')"
        v-model="survey.record.data.freq_mod_car"
        :min="0"
        :max="5"
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
    <div v-if="survey.stepName === 'trav_pro'">
      <ChoiceItem
        :label="t('form.trav_pro')"
        :options="travProOptions"
        v-model="survey.record.data.trav_pro"
        multiple
        :option-label-class="q.screen.lt.sm ? 'text-h5' : ''"
      />
    </div>
    <div v-if="survey.stepName === 'freq_mod_pro_local'">
      <SectionItem
        :label="t('form.freq_trav_pro_local_hint')"
        label-class="text-h2 text-green-2"
        class="q-mb-lg"
      />
      <SectionItem
        :label="t('form.freq_mod_pro')"
        :hint="t('form.days_per_month')"
        class="q-mb-lg"
      />
      <div class="row q-col-gutter-md q-mb-md">
        <div class="col-xs-12 col-sm-6">
          <NumberItem
            :label="t('form.mode.walking')"
            v-model="survey.record.data.freq_mod_pro_local_walking"
            :min="0"
            :max="30"
            :step="1"
            :step2="5"
            label-class="text-subtitle1 text-center"
            class="bg-primary rounded-borders q-pa-md"
          />
        </div>
        <div class="col-xs-12 col-sm-6">
          <NumberItem
            :label="t('form.mode.bike')"
            v-model="survey.record.data.freq_mod_pro_local_bike"
            :min="0"
            :max="30"
            :step="1"
            :step2="5"
            label-class="text-subtitle1 text-center"
            class="bg-primary rounded-borders q-pa-md"
          />
        </div>
      </div>
      <div class="row q-col-gutter-md q-mb-md">
        <div class="col-xs-12 col-sm-6">
          <NumberItem
            :label="t('form.mode.pub')"
            v-model="survey.record.data.freq_mod_pro_local_pub"
            :min="0"
            :max="30"
            :step="1"
            :step2="5"
            label-class="text-subtitle1 text-center"
            class="bg-primary rounded-borders q-pa-md"
          />
        </div>
        <div class="col-xs-12 col-sm-6">
          <NumberItem
            :label="t('form.mode.train')"
            v-model="survey.record.data.freq_mod_pro_local_train"
            :min="0"
            :max="30"
            :step="1"
            :step2="5"
            label-class="text-subtitle1 text-center"
            class="bg-primary rounded-borders q-pa-md"
          />
        </div>
      </div>
      <div class="row q-col-gutter-md q-mb-md">
        <div class="col-xs-12 col-sm-6">
          <NumberItem
            :label="t('form.mode.moto')"
            v-model="survey.record.data.freq_mod_pro_local_moto"
            :min="0"
            :max="30"
            :step="1"
            :step2="5"
            label-class="text-subtitle1 text-center"
            class="bg-primary rounded-borders q-pa-md"
          />
        </div>
        <div class="col-xs-12 col-sm-6">
          <NumberItem
            :label="t('form.mode.car')"
            v-model="survey.record.data.freq_mod_pro_local_car"
            :min="0"
            :max="30"
            :step="1"
            :step2="5"
            label-class="text-subtitle1 text-center"
            class="bg-primary rounded-borders q-pa-md"
          />
        </div>
      </div>
      <ToggleItem
        :label="t('form.mode.combined')"
        :left-label="t('form.no')"
        :right-label="t('form.yes')"
        v-model="survey.record.data.freq_mod_pro_local_combined"
        class="q-mt-xl q-mb-lg"
      />
    </div>
    <div v-if="survey.stepName === 'freq_mod_pro_region'">
      <SectionItem
        :label="t('form.freq_trav_pro_region_hint')"
        label-class="text-h2 text-green-2"
        class="q-mb-lg"
      />
      <SectionItem
        :label="t('form.freq_mod_pro')"
        :hint="t('form.days_per_month')"
        class="q-mb-lg"
      />
      <div class="row q-col-gutter-md q-mb-md">
        <div class="col-xs-12 col-sm-6">
          <NumberItem
            :label="t('form.mode.pub')"
            v-model="survey.record.data.freq_mod_pro_region_pub"
            :min="0"
            :max="30"
            :step="1"
            :step2="5"
            label-class="text-subtitle1 text-center"
            class="bg-primary rounded-borders q-pa-md"
          />
        </div>
        <div class="col-xs-12 col-sm-6">
          <NumberItem
            :label="t('form.mode.train')"
            v-model="survey.record.data.freq_mod_pro_region_train"
            :min="0"
            :max="30"
            :step="1"
            :step2="5"
            label-class="text-subtitle1 text-center"
            class="bg-primary rounded-borders q-pa-md"
          />
        </div>
      </div>
      <div class="row q-col-gutter-md q-mb-md">
        <div class="col-xs-12 col-sm-6">
          <NumberItem
            :label="t('form.mode.moto')"
            v-model="survey.record.data.freq_mod_pro_region_moto"
            :min="0"
            :max="30"
            :step="1"
            :step2="5"
            label-class="text-subtitle1 text-center"
            class="bg-primary rounded-borders q-pa-md"
          />
        </div>
        <div class="col-xs-12 col-sm-6">
          <NumberItem
            :label="t('form.mode.car')"
            v-model="survey.record.data.freq_mod_pro_region_car"
            :min="0"
            :max="30"
            :step="1"
            :step2="5"
            label-class="text-subtitle1 text-center"
            class="bg-primary rounded-borders q-pa-md"
          />
        </div>
      </div>
      <div class="row q-col-gutter-md q-mb-md">
        <div class="col-xs-12 col-sm-6">
          <NumberItem
            :label="t('form.mode.plane')"
            v-model="survey.record.data.freq_mod_pro_region_plane"
            :min="0"
            :max="30"
            :step="1"
            :step2="5"
            label-class="text-subtitle1 text-center"
            class="bg-primary rounded-borders q-pa-md"
          />
        </div>
        <div class="col-xs-12 col-sm-6"></div>
      </div>
      <ToggleItem
        :label="t('form.mode.combined')"
        :left-label="t('form.no')"
        :right-label="t('form.yes')"
        v-model="survey.record.data.freq_mod_pro_region_combined"
        class="q-mt-xl q-mb-lg"
      />
    </div>
    <div v-if="survey.stepName === 'freq_mod_pro_inter'">
      <SectionItem
        :label="t('form.freq_trav_pro_inter_hint')"
        label-class="text-h2 text-green-2"
        class="q-mb-lg"
      />
      <SectionItem
        :label="t('form.freq_mod_pro')"
        :hint="t('form.days_per_month')"
        class="q-mb-lg"
      />
      <div class="row q-col-gutter-md q-mb-md">
        <div class="col-xs-12 col-sm-6">
          <NumberItem
            :label="t('form.mode.car')"
            v-model="survey.record.data.freq_mod_pro_inter_car"
            :min="0"
            :max="30"
            :step="1"
            :step2="5"
            label-class="text-subtitle1 text-center"
            class="bg-primary rounded-borders q-pa-md"
          />
        </div>
        <div class="col-xs-12 col-sm-6">
          <NumberItem
            :label="t('form.mode.train')"
            v-model="survey.record.data.freq_mod_pro_inter_train"
            :min="0"
            :max="30"
            :step="1"
            :step2="5"
            label-class="text-subtitle1 text-center"
            class="bg-primary rounded-borders q-pa-md"
          />
        </div>
      </div>
      <div class="row q-col-gutter-md q-mb-md">
        <div class="col-xs-12 col-sm-6">
          <NumberItem
            :label="t('form.mode.plane')"
            v-model="survey.record.data.freq_mod_pro_inter_plane"
            :min="0"
            :max="30"
            :step="1"
            :step2="5"
            label-class="text-subtitle1 text-center"
            class="bg-primary rounded-borders q-pa-md"
          />
        </div>
        <div class="col-xs-12 col-sm-6"></div>
      </div>
      <ToggleItem
        :label="t('form.mode.combined')"
        :left-label="t('form.no')"
        :right-label="t('form.yes')"
        v-model="survey.record.data.freq_mod_pro_inter_combined"
        class="q-mt-xl q-mb-lg"
      />
    </div>
    <div v-if="survey.stepName === 'importance'">
      <SectionItem
        :label="t('form.importance')"
        :hint="t('form.importance_hint')"
        class="q-mb-lg"
      />
      <div class="row">
        <div class="col-sm-12 col-md-6">
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
        </div>
        <div class="col-sm-12 col-md-6">
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
      </div>
    </div>
    <div v-if="survey.stepName === 'needs'">
      <SectionItem :label="t('form.needs')" :hint="t('form.needs_hint')" class="q-mb-lg" />
      <div class="row">
        <div class="col-sm-12 col-md-6">
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
        </div>
        <div class="col-sm-12 col-md-6">
          <RatingItem
            :label="t('form.mode.train')"
            v-model="survey.record.data.needs_train"
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
        </div>
      </div>
    </div>
    <div v-if="survey.stepName === 'adjectives_bike'">
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
    <div v-if="survey.stepName === 'adjectives_pub_train'">
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
    <div v-if="survey.stepName === 'adjectives_car_moto'">
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
    <div v-if="survey.stepName === 'recommendations'">
      <RecommendationsPanel />
      <InfoPanel class="q-mt-lg" />
    </div>
    <div v-if="survey.stepName === 'comments'">
      <SectionItem :label="t('form.comments')" class="q-mb-lg" />
      <q-input
        v-model="survey.record.data.comments"
        type="textarea"
        class="q-mb-lg text-h6"
        bg-color="green-3"
        filled
      />
      <InfoPanel />
    </div>
    <div v-if="survey.stepName === 'final'">
      <FinalPanel />
    </div>
    <div class="row justify-center q-mt-xl">
      <q-btn
        rounded
        v-if="survey.isAfterStep('agreement') && survey.stepName !== 'final'"
        color="accent"
        icon="keyboard_arrow_left"
        size="lg"
        :title="t('previous')"
        @click="prevStep"
        class="q-mr-md"
      />
      <q-btn
        rounded
        v-if="survey.isBeforeStep('comments')"
        color="accent"
        icon="keyboard_arrow_right"
        size="lg"
        :title="t('next')"
        @click="nextStep"
        class="q-ml-md"
      />
      <q-btn
        rounded
        v-if="survey.stepName === 'comments'"
        color="primary"
        :label="t('finish')"
        icon-right="send"
        size="lg"
        @click="onSendComments"
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
import InfoPanel from 'src/components/form/InfoPanel.vue'
import FinalPanel from 'src/components/form/FinalPanel.vue'
import { notifyError } from 'src/utils/notify'

const { t, locale } = useI18n()
const survey = useSurvey()
const collector = useCollector()
const q = useQuasar()

const ageOptions = computed<Option[]>(() => [
  { value: '16-24', label: t('form.age_class_option.16_24') },
  { value: '25-44', label: t('form.age_class_option.25_44') },
  { value: '45-64', label: t('form.age_class_option.45_64') },
  { value: '65+', label: t('form.age_class_option.65') },
])

const equipmentsOptions = computed<Option[]>(() => [
  { value: 'bike', label: t('form.equipments_option.bike') },
  { value: 'ebike', label: t('form.equipments_option.ebike') },
  { value: 'upt_subs', label: t('form.equipments_option.upt_subs') },
  { value: 'train_subs', label: t('form.equipments_option.train_subs') },
  { value: 'mob_subs', label: t('form.equipments_option.mob_subs') },
  { value: 'moto', label: t('form.equipments_option.moto') },
  { value: 'car_driver', label: t('form.equipments_option.car_driver') },
  { value: 'car_passenger', label: t('form.equipments_option.car_passenger') },
])

const constraintsOptions = computed<Option[]>(() => [
  { value: 'dependent', label: t('form.constraints_option.dependent') },
  { value: 'heavy', label: t('form.constraints_option.heavy') },
  { value: 'night', label: t('form.constraints_option.night') },
  { value: 'disabled', label: t('form.constraints_option.disabled') },
])

const travProOptions = computed<Option[]>(() => [
  {
    value: 'local',
    label: t('form.trav_pro_option.local'),
    hint: t('form.trav_pro_option.local_hint'),
  },
  {
    value: 'region',
    label: t('form.trav_pro_option.region'),
    hint: t('form.trav_pro_option.region_hint'),
  },
  {
    value: 'inter',
    label: t('form.trav_pro_option.inter'),
    hint: t('form.trav_pro_option.inter_hint'),
  },
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
  if (survey.stepName === 'agreement') {
    if (!survey.record.data.terms_conditions) {
      notifyError(t('form.error.terms_conditions'))
      return
    }
    if (!survey.record.data.confidentiality) {
      notifyError(t('form.error.confidentiality'))
      return
    }
  }
  if (survey.stepName === 'places') {
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
    if (survey.stepName === 'recommendations') {
      survey.recommendation = {}
      survey.record.data.comments = ''
      collector
        .save(survey.tokenOrSlug, survey.record)
        .then(() => {
          void collector.loadInfo(survey.record.token)
          return collector.loadTypo(survey.record, locale.value)
        })
        .then((resp) => {
          survey.recommendation = resp
        })
        .catch(notifyError)
    } else if (survey.isBeforeStep('recommendations')) {
      void collector.save(survey.tokenOrSlug, survey.record).catch(console.error)
    }
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function prevStep() {
  if (survey.stepName === 'agreement') return
  survey.decStep()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function handleSwipe(dir: any) {
  if (survey.stepName === 'places') {
    // ignore because of map dragging conflict
    return
  }
  if (dir['direction'] === 'left') {
    nextStep()
  } else if (dir['direction'] === 'right') {
    prevStep()
  }
}

function onSendComments() {
  if (survey.tokenOrSlug) {
    void collector
      .saveComments(survey.record)
      .catch(console.error)
      .finally(() => {
        nextStep()
      })
  }
}
</script>
