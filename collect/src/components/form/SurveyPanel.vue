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
    <div v-if="survey.stepName === 'intermodality'">
      <JourneysPanel />
    </div>
    <div v-if="survey.stepName === 'travel_pro'">
      <ToggleItem
        :label="t('form.travel_pro')"
        v-model="survey.record.data.travel_pro"
        :left-label="t('form.no')"
        :right-label="t('form.yes')"
      />
    </div>
    <div v-if="survey.stepName === 'freq_mod_pro'">
      <ProJourneysPanel
        v-model="survey.record.data.freq_mod_pro_journeys"
        :modes="['walking', 'bike', 'pub', 'moto', 'car', 'train', 'boat', 'plane']"
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
    <div v-if="survey.stepName === 'recommendations'">
      <RecommendationsPanel />
      <InfoPanel class="q-mt-lg" />
    </div>
    <div v-if="survey.stepName === 'change' && survey.record.data.change">
      <SectionItem
        :label="t('form.change', { reco: t(`reco.${firstRecoDt}`) })"
        label-class="text-h4"
        class="q-mb-lg"
      />
      <RatingItem
        v-if="isRecoChange"
        :label="t('form.change_motivation')"
        :hint="t('form.change_motivation_hint')"
        v-model="survey.record.data.change.motivation"
        :max="5"
        label-class="text-h5"
        class="q-mb-lg"
        @update:model-value="onSave"
      />
      <ChoiceItem
        :label="t('form.change_levers')"
        :options="[
          { value: 'finance', label: t('form.change_levers_option.financial_support') },
          { value: 'flexibility', label: t('form.change_levers_option.work_flexibility') },
          { value: 'collective', label: t('form.change_levers_option.collective_changes') },
          { value: 'environment', label: t('form.change_levers_option.work_environment') },
          { value: 'other', label: t('form.change_levers_option.other') },
        ]"
        v-model="survey.record.data.change.levers"
        multiple
        label-class="text-h5"
        option-label-class="text-h5"
        @update:model-value="onSave"
      />
      <q-input
        v-if="survey.record.data.change.levers?.includes('other')"
        v-model="survey.record.data.change.other_levers"
        :label="t('form.change_other_levers_specify')"
        type="textarea"
        class="q-mb-lg text-h6"
        bg-color="green-3"
        filled
        debounce="500"
        @update:model-value="onSave"
      />
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
import type { Option } from 'src/components/form/models'
import ChoiceItem from 'src/components/form/ChoiceItem.vue'
import JourneysPanel from 'src/components/form/JourneysPanel.vue'
import ProJourneysPanel from 'src/components/form/ProJourneysPanel.vue'
import NumberItem from 'src/components/form/NumberItem.vue'
import ToggleItem from 'src/components/form/ToggleItem.vue'
import SectionItem from 'src/components/form/SectionItem.vue'
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
  { value: 'car', label: t('form.equipments_option.car') },
  { value: 'ev', label: t('form.equipments_option.ev') },
])

const constraintsOptions = computed<Option[]>(() => [
  { value: 'dependent', label: t('form.constraints_option.dependent') },
  { value: 'heavy', label: t('form.constraints_option.heavy') },
  { value: 'night', label: t('form.constraints_option.night') },
  { value: 'disabled', label: t('form.constraints_option.disabled') },
  { value: 'none', label: t('form.constraints_option.none'), exclusive: true },
])

const firstRecoDt = computed(() =>
  survey.recommendation.reco && survey.recommendation.reco.reco_dt2.length
    ? survey.recommendation.reco.reco_dt2[0]
    : '',
)

const isRecoChange = computed(() => !survey.isModeInRecommendation(survey.getMainFreqMod()))

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
  if (survey.stepName === 'intermodality') {
    for (const journey of survey.record.data.freq_mod_journeys || []) {
      if (journey.modes === undefined || journey.modes.length === 0) {
        notifyError(t('form.error.journey_mode'))
        return
      }
    }
  }
  if (survey.stepName === 'freq_mod_pro') {
    const errors: string[] = []
    for (const journey of survey.record.data.freq_mod_pro_journeys || []) {
      if (journey.mode === undefined || journey.mode === '') {
        errors.push(t('form.error.pro_journey_mode'))
      }
      if (journey.hex_id === undefined || journey.hex_id === '') {
        errors.push(t('form.error.pro_journey_hex_id'))
      }
    }
    if (errors.length) {
      errors.forEach((err) => notifyError(err))
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
    } else if (survey.stepName === 'change') {
      if (survey.record.data.change === undefined) {
        survey.record.data.change = {}
      }
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
  if (
    ['places', 'intermodality', 'freq_mod_pro', 'recommendations'].includes(survey.stepName || '')
  ) {
    // ignore because of map dragging conflict
    return
  }
  if (dir['direction'] === 'left') {
    nextStep()
  } else if (dir['direction'] === 'right') {
    prevStep()
  }
}

function onSave() {
  if (survey.tokenOrSlug) {
    if (survey.record.data.change.levers?.includes('other') === false) {
      survey.record.data.change.other_levers = undefined
    }
    void collector.save(survey.tokenOrSlug, survey.record).catch(console.error)
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
