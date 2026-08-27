<template>
  <div>
    <SectionItem :label="t('form.change')" label-class="text-h4" class="q-mb-md" />

    <q-card class="bg-primary-muted q-mb-xl">
      <q-card-section class="q-pa-sm">
        <div class="text-h5 text-secondary text-center">
          {{ t(`reco.${recoInter}`) }}
        </div>
      </q-card-section>
    </q-card>

    <div v-if="change">
      <RatingItem
        v-if="isRecoChange"
        :label="t('form.change_motivation')"
        :hint="t('form.change_motivation_hint')"
        v-model="change.motivation"
        :max="5"
        label-class="text-h4 text-bold q-mb-md"
        class="q-mb-lg"
        @update:model-value="onSave"
      />
      <ChoiceItem
        :label="t('form.change_levers')"
        :options="changeOptions"
        v-model="change.levers"
        multiple
        label-class="text-h4 text-bold q-mb-md"
        option-label-class="text-h5"
        @update:model-value="onSave"
      />
      <q-input
        v-if="change.levers?.includes('other')"
        v-model="change.other_levers"
        :label="t('form.change_other_levers_specify')"
        type="textarea"
        class="q-mb-lg text-h6"
        color="filled"
        bg-color="filled"
        outlined
        rounded
        debounce="500"
        @update:model-value="onSave"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import SectionItem from '@/components/form/SectionItem.vue'
import RatingItem from '@/components/form/RatingItem.vue'
import ChoiceItem from '@/components/form/ChoiceItem.vue'

const { t } = useI18n()
const survey = useSurvey()

interface Props {
  idx: number
}
const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

// Ensure a Change entry exists for this recommendation index before it's bound to.
watch(
  () => props.idx,
  (idx) => {
    if (!survey.record.data.changes) survey.record.data.changes = []
    if (!survey.record.data.changes[idx]) {
      survey.record.data.changes[idx] = {}
    }
  },
  { immediate: true },
)

const change = computed(() => survey.record.data.changes?.[props.idx])

const isRecoChange = computed(() => !survey.isRecommendationAtIndexInUse(props.idx))

const recoInter = computed(() =>
  survey.recommendation.reco?.reco_inter && survey.recommendation.reco.reco_inter.length
    ? (survey.recommendation.reco.reco_inter[props.idx] ?? '')
    : '',
)

const changeOptions = computed(() => {
  // if marche: no test
  const opts = []

  if (recoInter.value !== 'elec') {
    opts.push({
      value: 'flexibility',
      label: t('form.change_levers_option.work_flexibility'),
      hint: t('form.change_levers_option.work_flexibility_hint'),
    })
  }
  if (recoInter.value !== 'marche') {
    opts.push({
      value: 'test',
      label: t('form.change_levers_option.test'),
      hint: t('form.change_levers_option.test_hint'),
    })
  }
  if (!['elec', 'covoit'].includes(recoInter.value)) {
    opts.push({
      value: 'coaching',
      label: t('form.change_levers_option.coaching'),
    })
  }
  if (!['tpu', 'elec', 'inter_tim_tp'].includes(recoInter.value)) {
    opts.push({
      value: 'events',
      label: t('form.change_levers_option.events'),
      hint: t('form.change_levers_option.events_hint'),
    })
  }
  if (!['tpu', 'covoit', 'inter_tim_tp'].includes(recoInter.value)) {
    opts.push({
      value: 'environment',
      label: t('form.change_levers_option.work_environment'),
      hint: t('form.change_levers_option.work_environment_hint'),
    })
  }
  if (recoInter.value !== 'elec') {
    opts.push({
      value: 'company_vehicle',
      label: t('form.change_levers_option.company_vehicle'),
      hint: t('form.change_levers_option.company_vehicle_hint'),
    })
  }
  if (recoInter.value !== 'covoit') {
    opts.push({
      value: 'finance',
      label: t('form.change_levers_option.financial_support'),
      hint: t('form.change_levers_option.financial_support_hint'),
    })
  }
  opts.push({
    value: 'other',
    label: t('form.change_levers_option.other'),
  })
  return opts
})

function onSave() {
  emit('update:modelValue')
}
</script>
