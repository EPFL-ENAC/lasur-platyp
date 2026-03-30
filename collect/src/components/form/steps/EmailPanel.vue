<template>
  <div>
    <SectionItem :label="t('form.email.title')" label-class="text-h4" class="q-mb-md" />
    <q-card class="bg-primary q-mb-xl">
      <q-card-section class="q-pa-sm">
        <q-markdown class="text-h6" :src="t(`form.email.text`)" />
      </q-card-section>
      <q-card-section>
        <q-input
          v-model="email"
          :label="t('form.email.label')"
          class="q-mb-lg text-h6"
          bg-color="green-3"
          filled
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
