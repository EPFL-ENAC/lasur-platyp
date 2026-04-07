<template>
  <div>
    <SectionItem :label="t('form.email.title')" label-class="text-h4" class="q-mb-md" />

    <q-card flat class="q-mb-xl">
      <q-card-section>
        <q-markdown class="text-h6" :src="t(`form.email.text`)" />
      </q-card-section>
      <q-card-section>
        <q-input
          v-model="email"
          :label="t('form.email.label')"
          class="q-mb-lg text-h6"
          color="field"
          outlined
          rounded
        />
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import SectionItem from 'src/components/form/SectionItem.vue'

const email = defineModel<string>()

const { t } = useI18n()
</script>
