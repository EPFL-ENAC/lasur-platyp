<template>
  <q-select
    multiple
    emit-value
    map-options
    rounded
    outlined
    color="field"
    dropdown-icon="expand_more"
    :model-value="modelValue"
    :options="options"
    :display-value="displayValue"
    :disable="disable"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <template v-slot:prepend>
      <q-icon
        v-if="modelValue.length > 0"
        name="close"
        class="clear-icon"
        role="button"
        tabindex="0"
        :aria-label="t('deselect')"
        @click.stop="emit('update:modelValue', [])"
        @keyup.enter.stop="emit('update:modelValue', [])"
      />
    </template>
    <template v-slot:option="{ itemProps, opt, selected }">
      <q-item v-bind="itemProps">
        <q-item-section>
          <q-item-label>{{ opt.label }}</q-item-label>
        </q-item-section>
        <q-item-section v-if="selected" side>
          <q-icon name="check" />
        </q-item-section>
      </q-item>
    </template>
  </q-select>
</template>

<script setup lang="ts">
export interface FilterOption {
  label: string
  value: string | number | undefined
}

interface Props {
  modelValue: (string | number)[]
  options: FilterOption[]
  displayValue: string
  disable?: boolean
}
defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: (string | number)[]]
}>()

const { t } = useI18n()
</script>

<style scoped lang="scss">
.clear-icon {
  color: $brand-yellow-400;
  font-size: 20px;
  padding: 8px 8px 8px 0;
  cursor: pointer;
}
</style>
