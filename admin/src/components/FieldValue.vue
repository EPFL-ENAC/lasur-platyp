<template>
  <span>
    <template v-if="value === null || value === undefined">-</template>
    <template v-else-if="typeof value === 'number'">{{ toMaxDecimals(value, 3) }}</template>
    <template v-else-if="typeof value === 'boolean'">
      <q-icon
        :name="value ? 'check_circle' : 'cancel'"
        :color="value ? 'green' : 'red'"
        size="xs"
      />
    </template>
    <template v-else-if="Array.isArray(value)">
      <ol style="padding-left: 15px">
        <li v-for="(val, index) in value" :key="index">
          <FieldValue :value="val" />
        </li>
      </ol>
    </template>
    <template v-else-if="typeof value === 'object'">
      <ul style="padding-left: 15px">
        <template v-for="(val, key) in value" :key="key">
          <li>
            <strong>{{ key }}</strong
            >:
            <FieldValue :value="val" />
          </li>
        </template>
      </ul>
    </template>
    <template v-else>{{ value }}</template>
  </span>
</template>
<script setup lang="ts">
import { toMaxDecimals } from 'src/utils/numbers'

defineOptions({
  name: 'FieldValue',
})

export interface Props {
  value: string | number | boolean | null | undefined | unknown | Record<string, unknown>
}
defineProps<Props>()
</script>
