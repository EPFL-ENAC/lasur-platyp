<template>
  <q-page class="bg-secondary text-white">
    <q-linear-progress
      v-if="survey.started"
      size="10px"
      :value="progress"
      color="accent"
      :animation-speed="200"
      class="q-mb-md"
    />
    <div class="container">
      <div class="content q-pa-lg">
        <div v-if="collector.loading">
          <q-spinner-grid color="white" size="50px" />
        </div>
        <div v-else>
          <div v-if="survey.started">
            <SurveyPanel v-if="survey.record" />
          </div>
          <div v-else>
            <div class="text-h4 q-mb-md">
              {{ t('welcome', { brand: t('main.brand') }) }}
            </div>
            <div class="text-h6 q-mb-md">
              {{ t('welcome_intro') }}
            </div>
            <div v-if="survey.step > 1">
              <q-btn
                rounded
                icon-right="play_arrow"
                color="accent"
                :label="t('resume')"
                size="lg"
                @click="survey.started = true"
                class="q-mt-md on-left"
              />
              <q-btn
                flat
                icon-right="restart_alt"
                color="accent"
                no-caps
                :label="t('start_new')"
                size="lg"
                @click="reset()"
                class="q-mt-md"
              />
            </div>
            <div v-else>
              <div v-if="route.params.token === undefined">
                <q-input
                  v-model="tkSlug"
                  :label="t('token')"
                  outlined
                  dark
                  color="white"
                  class="text-white"
                  debounce="300"
                  @update:model-value="onToken"
                />
              </div>
              <q-btn
                rounded
                icon-right="play_arrow"
                color="accent"
                :label="t('start')"
                size="lg"
                @click="onStart"
                :disable="survey.tokenOrSlug === null"
                class="q-mt-md"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import SurveyPanel from 'src/components/form/SurveyPanel.vue'
import { notifyError } from 'src/utils/notify'
import type { Record } from 'src/models'

const { t } = useI18n()
const route = useRoute()
const collector = useCollector()
const survey = useSurvey()

const tkSlug = ref('')

const progress = computed(() => {
  return survey.step / survey.stepNames.length
})

onMounted(onInit)

watch(
  () => survey.started,
  async (value) => {
    if (value === false) {
      await onInit()
    }
  },
)

async function onInit() {
  if (route.params.token) {
    tkSlug.value = route.params.token as string
    if (survey.record?.token === undefined) {
      await onToken()
    }
    if (survey.tokenOrSlug !== tkSlug.value) {
      await reset()
    }
  }
}

async function onToken() {
  if (tkSlug.value && tkSlug.value.trim().length > 0) {
    return collector
      .load(tkSlug.value.trim())
      .then((cr: Record) => {
        survey.tokenOrSlug = tkSlug.value.trim()
        survey.init(cr)
      })
      .catch(notifyError)
  }
  return Promise.resolve()
}

async function reset() {
  survey.reset()
  await onToken()
}

function onStart() {
  survey.started = true
  survey.step = 1
  tkSlug.value = ''
}
</script>
