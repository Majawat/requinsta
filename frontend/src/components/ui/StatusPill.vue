<template>
  <span class="pill" :class="[meta.pill, small ? 'px-2 py-0.5 text-[11px] gap-1' : '']">
    <span class="rounded-full" :class="[meta.dot, small ? 'w-[5px] h-[5px]' : 'w-1.5 h-1.5']"></span>
    {{ label || meta.label }}
  </span>
</template>

<script>
import { computed } from 'vue'
import { statusMeta } from '../../utils/requestUtils'

export default {
  name: 'StatusPill',
  props: {
    status: { type: String, required: true },
    // Optional plain-language override, e.g. "Pending review", "Downloading".
    label: { type: String, default: '' },
    small: { type: Boolean, default: false },
  },
  setup(props) {
    return { meta: computed(() => statusMeta(props.status)) }
  },
}
</script>
