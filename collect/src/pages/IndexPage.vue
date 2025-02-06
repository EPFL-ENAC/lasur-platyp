<template>
  <q-page class="bg-secondary text-white">
    <div class="container">
      <div class="content q-pa-lg">
        <div v-if="collector.loading">
          <q-spinner-grid color="white" size="50px" />
        </div>
        <div v-else>
          <div v-if="started">
            <SurveyPanel v-if="collector.participantData" />
          </div>
          <div v-else>
            <div class="text-h4 q-mb-md">
              {{ t('welcome', { brand: t('main.brand') }) }}
            </div>
            <div class="text-h6 q-mb-md">
              {{ t('welcome_intro') }}
            </div>
            <div v-if="route.params.token === undefined">
              <q-input
                v-model="tk"
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
              color="primary"
              :label="t('start')"
              size="lg"
              @click="started = true"
              :disable="!collector.token"
              class="q-mt-md"
            />
          </div>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import SurveyPanel from 'src/components/form/SurveyPanel.vue'
import { notifyError } from 'src/utils/notify'

const { t } = useI18n()
const route = useRoute()
const collector = useCollector()

const tk = ref('')
const started = ref(false)

onMounted(() => {
  if (route.params.token) {
    tk.value = route.params.token as string
    onToken()
  }
})

function onToken() {
  if (tk.value && tk.value.trim().length > 0) {
    collector
      .loadToken(tk.value.trim())
      .then(() => {
        console.log(collector.caseReport)
      })
      .catch(notifyError)
  }
}
</script>
