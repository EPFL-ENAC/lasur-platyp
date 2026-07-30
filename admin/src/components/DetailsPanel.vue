<template>
  <div>
    <a
      v-if="!inline"
      href="#"
      class="q-mb-md text-secondary row items-center inline-flex no-wrap"
      @click.prevent="onToggleDetails"
    >
      {{ showDetails ? t('read_less') : t('read_more') }}
      <q-icon :name="showDetails ? 'keyboard_arrow_up' : 'keyboard_arrow_down'" />
    </a>
    <slot v-if="inline || showDetails" />
  </div>
</template>

<script setup lang="ts">
const { t } = useI18n()

interface Props {
  inline?: boolean
}

defineProps<Props>()

const showDetails = ref(false)

const onToggleDetails = () => {
  showDetails.value = !showDetails.value
}
</script>
