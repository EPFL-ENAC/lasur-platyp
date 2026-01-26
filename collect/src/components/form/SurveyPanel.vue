<template>
  <div v-if="survey.record" v-touch-swipe.mouse.left.right="handleSwipe">
    <!--pre>{{ survey.step }} - {{ survey.stepName }}</pre-->
    <div v-if="survey.stepName === 'agreement'">
      <SectionItem :label="t('form.agreement')" :hint="t('form.agreement_hint')" class="q-mb-lg" />
      <AgreementPanel />
    </div>
    <div v-if="survey.stepName === 'age_class'">
      <AgePanel />
    </div>
    <div v-if="survey.stepName === 'employment'">
      <EmploymentPanel />
    </div>
    <div v-if="survey.stepName === 'places'">
      <div class="text-h4 text-bold">{{ t('form.workplace') }}</div>
      <PlacesPanel />
    </div>
    <div v-if="survey.stepName === 'travel_time'">
      <TravelTimePanel />
    </div>
    <div v-if="survey.stepName === 'constraints'">
      <ConstraintsPanel />
    </div>
    <div v-if="survey.stepName === 'equipments'">
      <EquipmentsPanel />
    </div>
    <div v-if="survey.stepName === 'intermodality'">
      <JourneysPanel />
    </div>
    <div v-if="survey.stepName === 'travel_pro'">
      <TravelProPanel />
    </div>
    <div v-if="survey.stepName === 'freq_mod_pro'">
      <ProJourneysPanel
        v-model="survey.record.data.freq_mod_pro_journeys"
        :modes="[
          'walking',
          'bike',
          'cargo',
          'pub',
          'moto',
          'car',
          'truck',
          'train',
          'boat',
          'plane',
        ]"
      />
    </div>
    <div v-if="survey.stepName === 'importance'">
      <SectionItem
        :label="t('form.importance')"
        :hint="t('form.importance_hint')"
        class="q-mb-lg"
      />
      <ImportancePanel />
    </div>
    <div v-if="survey.stepName === 'needs'">
      <SectionItem :label="t('form.needs')" :hint="t('form.needs_hint')" class="q-mb-lg" />
      <NeedsPanel />
    </div>
    <div v-if="survey.stepName === 'recommendations'">
      <RecommendationsPanel />
      <InfoPanel class="q-mt-lg" />
    </div>
    <div v-if="survey.stepName === 'change'">
      <ChangePanel @update:modelValue="onSave" />
    </div>
    <div v-if="survey.stepName === 'change2'">
      <Change2Panel @update:modelValue="onSave" />
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
import SectionItem from 'src/components/form/SectionItem.vue'
import AgreementPanel from 'src/components/form/steps/AgreementPanel.vue'
import AgePanel from 'src/components/form/steps/AgePanel.vue'
import EmploymentPanel from 'src/components/form/steps/EmploymentPanel.vue'
import PlacesPanel from 'src/components/form/steps/PlacesPanel.vue'
import EquipmentsPanel from 'src/components/form/steps/EquipmentsPanel.vue'
import ConstraintsPanel from 'src/components/form/steps/ConstraintsPanel.vue'
import JourneysPanel from 'src/components/form/steps/JourneysPanel.vue'
import ProJourneysPanel from 'src/components/form/steps/ProJourneysPanel.vue'
import TravelTimePanel from 'src/components/form/steps/TravelTimePanel.vue'
import TravelProPanel from 'src/components/form/steps/TravelProPanel.vue'
import ImportancePanel from 'src/components/form/steps/ImportancePanel.vue'
import NeedsPanel from 'src/components/form/steps/NeedsPanel.vue'
import RecommendationsPanel from 'src/components/form/steps/RecommendationsPanel.vue'
import ChangePanel from 'src/components/form/steps/ChangePanel.vue'
import Change2Panel from 'src/components/form/steps/Change2Panel.vue'
import InfoPanel from 'src/components/form/steps/InfoPanel.vue'
import FinalPanel from 'src/components/form/steps/FinalPanel.vue'
import { notifyError } from 'src/utils/notify'

const { t, locale } = useI18n()
const survey = useSurvey()
const collector = useCollector()

onMounted(() => {
  if (survey.tokenOrSlug) {
    void collector.loadInfo(survey.record.token)
  }
})

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
    void collector.loadInfo(survey.record.token)
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
          survey.record.typo = resp
        })
        .catch(notifyError)
    } else if (survey.isBeforeStep('recommendations')) {
      void collector.save(survey.tokenOrSlug, survey.record).catch(console.error)
    } else if (survey.stepName === 'change') {
      if (survey.record.data.change === undefined) {
        survey.record.data.change = {}
      }
      void collector.save(survey.tokenOrSlug, survey.record).catch(console.error)
    } else if (survey.stepName === 'change2') {
      if (survey.record.data.change2 === undefined) {
        survey.record.data.change2 = {}
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
    if (survey.record.data.change?.levers?.includes('other') === false) {
      survey.record.data.change.other_levers = undefined
    }
    if (survey.record.data.change2?.levers?.includes('other') === false) {
      survey.record.data.change2.other_levers = undefined
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
