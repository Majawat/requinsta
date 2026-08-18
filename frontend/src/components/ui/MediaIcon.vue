<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    :stroke="color || icon.color"
    :stroke-width="strokeWidth"
    stroke-linecap="round"
    stroke-linejoin="round"
    v-html="icon.svg"
  />
</template>

<script>
import { computed } from 'vue'
import { mediaIcon } from '../../utils/requestUtils'

export default {
  name: 'MediaIcon',
  props: {
    type: { type: String, default: 'other' },
    size: { type: [Number, String], default: 16 },
    // Override the type colour (e.g. muted placeholder). Falls back to the
    // type's own colour.
    color: { type: String, default: '' },
    strokeWidth: { type: [Number, String], default: 1.8 },
  },
  setup(props) {
    return { icon: computed(() => mediaIcon(props.type)) }
  },
}
</script>
