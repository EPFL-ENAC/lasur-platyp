<template>
  <q-page class="row items-center justify-evenly bg-secondary text-white">
    <div>
      <div v-if="collector.loading">
        <q-spinner-grid color="white" size="50px" />
      </div>
      <div v-else>
        <div class="q-mb-md">
          {{ t('welcome', { brand: t('main.brand') }) }}
        </div>
        <div v-show="route.params.token === undefined">
          <q-input
            v-model="tk"
            :label="t('token')"
            outlined
            dark
            color="white"
            class="text-white"
            @keyup.enter="onToken"
          />
        </div>
        <div>
          <pre>{{ collector.participantData }}</pre>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { notifyError } from 'src/utils/notify'

const { t } = useI18n()
const route = useRoute()
const collector = useCollector()

const tk = ref('')

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
        console.log(collector.participantData)
      })
      .catch(notifyError)
  }
}
</script>
