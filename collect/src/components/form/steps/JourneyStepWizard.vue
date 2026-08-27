<template>
  <div class="journey-wizard">
    <transition name="fade" mode="out-in">
      <!-- Phase 1: Select mode (first or next) -->
      <div v-if="phase === 'select-mode'" :key="'select'">
        <div class="text-bold text-h5 q-mb-md">
          {{
            selectedModes.length === 0
              ? t('form.journey.step.first_mode')
              : t('form.journey.step.next_mode')
          }}
        </div>

        <div v-if="selectedModes.length > 0" class="row justify-center q-mb-lg">
          <div class="row items-center q-gutter-sm">
            <template v-for="(mode, idx) in selectedModes" :key="idx">
              <div class="row items-center journey-chip">
                <span class="text-h6 q-mr-sm">{{ getOptionLabel(mode) }}</span>
              </div>
              <q-icon name="arrow_forward" color="primary" size="sm" />
            </template>
          </div>
        </div>

        <div class="row justify-center q-gutter-md q-mt-lg">
          <template v-for="option in modeOptions" :key="option.value">
            <div v-if="!option.children || option.children.length === 0" class="text-center">
              <q-btn
                :title="option.label"
                color="secondary"
                size="xl"
                round
                class="journey-mode-btn bordered-secondary"
                @click="onSelectMode(option.value)"
              >
                <q-img
                  v-if="option.icon?.endsWith('.svg')"
                  :src="option.icon"
                  style="width: 36px; height: 36px"
                  no-spinner
                  no-transition
                  class="icon-white"
                />
                <q-icon v-else :name="option.icon" color="white" size="lg" />
              </q-btn>
              <div class="text-caption q-mt-sm">{{ option.label }}</div>
            </div>

            <div v-else class="text-center">
              <div v-if="!expandedParent[option.value]">
                <q-btn
                  :title="option.label"
                  color="secondary"
                  size="xl"
                  round
                  class="journey-mode-btn bordered-secondary"
                  @click="expandedParent[option.value] = true"
                >
                  <q-icon :name="option.icon" color="white" size="lg" />
                </q-btn>
                <div class="text-caption q-mt-sm">{{ option.label }}</div>
              </div>
              <div v-else class="q-card expand-panel">
                <div class="row justify-center q-gutter-sm q-pa-md">
                  <template v-for="child in option.children" :key="child.value">
                    <div class="text-center">
                      <q-btn
                        :title="child.label"
                        color="secondary"
                        size="lg"
                        round
                        class="journey-mode-btn bordered-secondary"
                        @click="onSelectMode(child.value)"
                      >
                        <q-img
                          v-if="child.icon?.endsWith('.svg')"
                          :src="child.icon"
                          style="width: 36px; height: 36px"
                          no-spinner
                          no-transition
                          class="icon-white"
                        />
                        <q-icon v-else :name="child.icon" color="white" size="lg" />
                      </q-btn>
                      <div class="text-caption q-mt-sm">{{ child.label }}</div>
                    </div>
                  </template>
                </div>
                <div class="row justify-center q-pb-md">
                  <q-btn
                    flat
                    size="sm"
                    color="primary"
                    :label="t('previous')"
                    @click="expandedParent[option.value] = false"
                  />
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- Phase 2: Switch confirm (Yes/No) -->
      <div v-else-if="phase === 'switch-confirm'" :key="'switch'">
        <div class="text-bold text-h5 q-mb-md">
          {{ t('form.journey.step.switch_question') }}
        </div>
        <div class="text-h6 q-mb-lg">{{ t('form.journey.step.switch_hint') }}</div>

        <div class="row justify-center q-gutter-md q-mt-lg">
          <q-btn
            unelevated
            rounded
            size="lg"
            color="primary"
            no-caps
            :label="t('form.yes')"
            class="q-px-xl"
            @click="onSwitchAnswer(true)"
          />
          <q-btn
            unelevated
            rounded
            size="lg"
            color="accent"
            no-caps
            :label="t('form.no')"
            class="q-px-xl"
            @click="onSwitchAnswer(false)"
          />
        </div>
      </div>

      <!-- Phase 3: Days slider -->
      <div v-else-if="phase === 'days'" :key="'days'">
        <div class="text-bold text-h5 q-mb-md">
          {{ t('form.journey.step.days_question') }}
        </div>

        <div class="row justify-center q-mb-lg">
          <div class="row items-center q-gutter-sm">
            <template v-for="(mode, idx) in selectedModes" :key="idx">
              <div class="row items-center journey-chip">
                <span class="text-h6">{{ getOptionLabel(mode) }}</span>
              </div>
              <q-icon
                v-if="idx < selectedModes.length - 1"
                name="arrow_forward"
                color="primary"
                size="sm"
              />
            </template>
          </div>
        </div>

        <SliderItem
          v-model="days"
          :label="t('form.journey.days_per_week')"
          :min="1"
          :max="5"
          label-class="text-h5"
          class="q-pa-sm"
        />

        <div class="row justify-center q-mt-lg">
          <q-btn
            unelevated
            rounded
            size="lg"
            color="primary"
            no-caps
            :label="t('form.journey.step.continue_label')"
            class="full-width"
            :style="{ maxWidth: '200px' }"
            @click="onContinue"
          />
        </div>
      </div>

      <!-- Phase 4: Review + Save -->
      <div v-else-if="phase === 'review'" :key="'review'">
        <div class="text-bold text-h5 q-mb-md">
          {{ t('form.journey.step.review_title') }}
        </div>

        <q-card flat bordered class="q-mb-lg">
          <q-card-section>
            <div class="row items-center q-gutter-sm q-mb-md">
              <template v-for="(mode, idx) in selectedModes" :key="idx">
                <div class="row items-center journey-chip-large">
                  <span class="text-h6">{{ getOptionLabel(mode) }}</span>
                </div>
                <q-icon
                  v-if="idx < selectedModes.length - 1"
                  name="arrow_forward"
                  color="primary"
                  size="md"
                />
              </template>
            </div>
            <div class="text-h5">
              {{ days }} {{ t('form.journey.days_per_week').toLowerCase() }}
            </div>
          </q-card-section>
        </q-card>

        <div class="row justify-center q-gutter-md">
          <q-btn
            unelevated
            rounded
            size="lg"
            color="primary"
            no-caps
            :label="t('form.journey.step.save')"
            class="q-px-xl"
            @click="onSave"
          />
        </div>
      </div>

      <!-- Phase 5: Add another -->
      <div v-else-if="phase === 'add-another'" :key="'add'">
        <div class="text-bold text-h5 q-mb-md">
          {{ t('form.journey.saved') }}
        </div>
        <div class="text-h6 q-mb-md">{{ t('form.journey.saved_detail') }}</div>

        <div class="row justify-center q-gutter-md q-mt-lg">
          <q-btn
            unelevated
            rounded
            size="lg"
            color="primary"
            no-caps
            :label="t('form.journey.step.add_yes')"
            class="q-px-xl"
            @click="onStartNewJourney"
          />
          <q-btn
            unelevated
            rounded
            size="lg"
            color="accent"
            no-caps
            :label="t('form.journey.step.add_no')"
            class="q-px-xl"
            @click="onDone"
          />
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import SliderItem from '@/components/form/SliderItem.vue'
import type { Option } from '@/components/form/models'

interface Props {
  label?: string
  hint?: string
}

defineProps<Props>()
const emit = defineEmits<{
  save: [journey: { modes: string[]; days: number }]
  done: []
}>()

const { t } = useI18n()

type Phase = 'select-mode' | 'switch-confirm' | 'days' | 'review' | 'add-another'

type PhaseState = {
  phase: Phase
  selectedModes: string[]
  days: number
  expandedParent: Record<string, boolean>
}

const state = ref<PhaseState>({
  phase: 'select-mode',
  selectedModes: [],
  days: 1,
  expandedParent: {},
})

const phase = computed(() => state.value.phase)
const selectedModes = computed(() => state.value.selectedModes)
const days = computed({
  get: () => state.value.days,
  set: (val: number) => {
    state.value.days = val
  },
})

const expandedParent = computed({
  get: () => state.value.expandedParent,
  set: (val: Record<string, boolean>) => {
    state.value.expandedParent = val
  },
})

const modeOptions = computed<Option[]>(() => [
  { value: 'walking', label: t('form.mode.walking'), icon: 'directions_walk' },
  {
    value: 'bike',
    label: t('form.mode.bike'),
    icon: 'directions_bike',
    children: [
      { value: 'bike', label: t('form.mode.bike'), icon: 'pedal_bike' },
      { value: 'ebike', label: t('form.mode.ebike'), icon: 'electric_bike' },
    ],
  },
  { value: 'pub', label: t('form.mode.pub'), icon: 'directions_bus' },
  { value: 'moto', label: t('form.mode.moto'), icon: 'two_wheeler' },
  {
    value: 'car',
    label: t('form.mode.car'),
    icon: 'directions_car',
    children: [
      { value: 'car', label: t('form.mode.car'), icon: 'directions_car' },
      {
        value: 'carpool',
        label: t('form.mode.carpool'),
        icon: '/icons/directions_carpool.svg',
      },
    ],
  },
  { value: 'train', label: t('form.mode.train'), icon: 'directions_railway' },
  {
    value: 'other',
    label: t('form.mode.other'),
    icon: '/icons/scooter.svg',
    hint: t('form.mode.other_hint'),
  },
])

function getOptionLabel(value: string) {
  for (const opt of modeOptions.value) {
    if (opt.value === value) return opt.label
    if (opt.children) {
      const child = opt.children.find((c) => c.value === value)
      if (child) return child.label
    }
  }
  return value
}

function onSelectMode(modeValue: string) {
  state.value.selectedModes.push(modeValue)
  state.value.expandedParent = {}

  if (state.value.selectedModes.length >= 5) {
    state.value.phase = 'days'
  } else {
    state.value.phase = 'switch-confirm'
  }
}

function onSwitchAnswer(wantsMore: boolean) {
  if (wantsMore) {
    state.value.phase = 'select-mode'
  } else {
    state.value.phase = 'days'
  }
}

function onContinue() {
  state.value.phase = 'review'
}

function onSave() {
  emit('save', {
    modes: [...state.value.selectedModes],
    days: state.value.days,
  })
  state.value.phase = 'add-another'
}

function onStartNewJourney() {
  state.value.phase = 'select-mode'
  state.value.selectedModes = []
  state.value.days = 1
  state.value.expandedParent = {}
}

function onDone() {
  emit('done')
}
</script>

<style scoped lang="scss">
.journey-wizard {
  min-height: 200px;
}

.expand-panel {
  display: inline-block;
  width: auto;
  min-width: 200px;
  max-width: 350px;
  margin: 0 auto;
}

.journey-chip {
  padding: 4px 8px;
  border: 1px solid var(--secondary-border-color);
  border-radius: 4px;
  background: var(--super-muted-color);
}

.journey-chip-large {
  padding: 8px 16px;
  border: 2px solid var(--secondary-border-color);
  border-radius: 8px;
  background: var(--super-muted-color);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
