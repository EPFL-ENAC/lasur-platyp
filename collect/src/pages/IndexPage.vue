<template>
  <q-page class="index-page" :class="{ 'index-page--survey': survey.started }">
    <div v-if="survey.started" class="survey-progress">
      <q-linear-progress
        size="8px"
        :value="progress"
        color="accent"
        :animation-speed="200"
        class="survey-progress__bar"
        :style="{ '--progress-value': progress }"
      />
    </div>
    <div class="container">
      <div class="content q-pa-lg">
        <div v-if="collector.loading">
          <q-spinner-grid color="white" size="50px" />
        </div>
        <div v-else>
          <div v-if="survey.started">
            <SurveyPanel v-if="survey.record" />
          </div>
          <div v-else class="welcome">
            <div class="welcome__eyebrow text-h6 text-weight-medium">
              {{ t('welcome_eyebrow') }}
            </div>
            <h1 class="welcome__title text-h2 text-weight-semibold">
              {{ t('welcome', { brand: t('main.brand') }) }}
            </h1>
            <p class="welcome__intro text-h5">
              {{ t('welcome_intro') }}
            </p>
            <div v-if="survey.step > 1">
              <q-btn
                icon-right="arrow_forward"
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
              <div v-if="route.params.token === undefined" class="welcome__token">
                <q-input
                  v-model="tkSlug"
                  :label="t('token')"
                  outlined
                  color="field"
                  debounce="300"
                  @update:model-value="onToken"
                />
              </div>
              <q-btn
                icon-right="arrow_forward"
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
    <div v-if="!survey.started" class="welcome__language">
      <span>{{ t('select_preferred_language') }}</span>
      <q-btn-dropdown flat :label="currentLocaleLabel" icon="language">
        <q-list>
          <q-item
            clickable
            v-close-popup
            @click="onLocaleSelection(localeOpt)"
            v-for="localeOpt in localeOptions"
            :key="localeOpt.value"
          >
            <q-item-section>
              <q-item-label>{{ localeOpt.label }}</q-item-label>
            </q-item-section>
            <q-item-section avatar v-if="locale === localeOpt.value">
              <q-icon color="primary" name="check" />
            </q-item-section>
          </q-item>
        </q-list>
      </q-btn-dropdown>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { Cookies } from 'quasar'
import { locales, localeLabel } from '@/boot/i18n'
import SurveyPanel from '@/components/form/SurveyPanel.vue'
import { notifyError } from '@/utils/notify'
import type { Record } from '@/models'

const { locale, t } = useI18n()
const route = useRoute()
const collector = useCollector()
const survey = useSurvey()

const tkSlug = ref('')

const progress = computed(() => {
  return survey.step / survey.stepNames.length
})
const localeOptions = computed(() => {
  return locales.map((key) => ({
    label: localeLabel(key),
    value: key,
  }))
})
const currentLocaleLabel = computed(() => localeLabel(locale.value))

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
      .loadRecordDraft(tkSlug.value.trim())
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
  if (!survey.tokenOrSlug) return
  survey.started = true
  survey.step = 1
  tkSlug.value = ''
  void collector.loadInfo(survey.tokenOrSlug)
}

function onLocaleSelection(localeOpt: { label: string; value: string }) {
  locale.value = localeOpt.value
  Cookies.set('locale', localeOpt.value)
}
</script>

<style scoped lang="scss">
// Page fills the viewport so the language selector can sit at its foot
.index-page {
  display: flex;
  flex-direction: column;
}

.index-page .container {
  flex: 1;
  min-height: 0;
}

// Aligned with the survey content: same max width and same lateral padding as
// `.content`, so the bar starts and ends on the text edges.
.survey-progress {
  width: 100%;
  max-width: 850px;
  margin: 96px auto 0;
  padding: 0 24px;
}

// While the survey runs the content sits right under the progress bar rather
// than being centred in the viewport, on a 96px gap.
.index-page--survey .container {
  align-items: start;
}

.index-page--survey .survey-progress {
  margin-bottom: 96px;
}

.index-page--survey .content {
  padding-top: 0;
}

.survey-progress__bar {
  border-radius: 999px; // pill, clips the track and both fill ends
  overflow: hidden;
}

// The fill is laid out full width and scaled down on X, which would squash a
// plain radius flat. Dividing the horizontal radius by the same factor lands it
// back at a true 4px round on screen.
.survey-progress__bar :deep(.q-linear-progress__model) {
  border-radius: calc(4px / max(var(--progress-value), 0.02)) / 4px;
}

.welcome {
  text-align: center;
}

.welcome__eyebrow {
  margin-bottom: 12px;
  color: $brand-yellow-700;
}

.welcome__title {
  margin: 0 0 36px;
  letter-spacing: -0.01em;
  color: $brand-purple-900;
}

.welcome__intro {
  max-width: 42rem;
  margin: 0 auto 48px;
  color: $brand-purple-400;
}

.welcome__token {
  max-width: 26rem;
  margin: 0 auto;
  text-align: left;
}

.welcome__language {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 24px 16px;
  color: $brand-purple-400;
}

.body--dark {
  .welcome__eyebrow {
    color: $brand-yellow-300;
  }

  .welcome__title {
    color: #fff;
  }

  .welcome__intro,
  .welcome__language {
    color: $brand-purple-100;
  }
}
</style>
