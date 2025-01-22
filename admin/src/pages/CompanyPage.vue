<template>
  <q-page>
    <div class="text-h5 q-pa-md">
      <q-breadcrumbs gutter="sm">
        <q-breadcrumbs-el :label="t('companies')" to="/companies" />
        <q-breadcrumbs-el :label="id + ''" />
      </q-breadcrumbs>
    </div>
    <q-separator />
    <div class="q-pa-md"></div>
  </q-page>
</template>

<script setup lang="ts">
const route = useRoute()
const { t } = useI18n()
const services = useServices()
const service = services.make('company')

const id = computed(() => route.params.id)

onMounted(() => {
  if (id.value === undefined) return
  service.get(id.value + '').then((company) => {
    console.log(company)
  })
})
</script>
