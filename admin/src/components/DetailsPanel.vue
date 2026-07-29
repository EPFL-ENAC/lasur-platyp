<template>
  <div>
    <a
      href="#"
      class="q-mb-md text-secondary row items-center inline-flex no-wrap"
      @click.prevent="onToggleDetails"
    >
      {{ showDetails ? t('less_details') : t('more_details') }}
      <q-icon :name="showDetails ? 'keyboard_arrow_up' : 'keyboard_arrow_down'" />
    </a>
    <slot v-if="showDetails" />
  </div>
</template>

<script setup lang="ts">
const { t } = useI18n()

const props = defineProps({
  showDetails: {
    type: Boolean,
    default: false,
  },
})

const showDetails = ref(props.showDetails)

const onToggleDetails = () => {
  showDetails.value = !showDetails.value
}
</script>
