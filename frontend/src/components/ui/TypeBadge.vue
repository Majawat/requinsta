<template>
  <span class="inline-flex items-center gap-1.5 px-2 py-1 rounded-md bg-slate-800 text-[11px] font-semibold text-slate-300">
    <MediaIcon :type="type" :size="12" />
    {{ label }}
  </span>
</template>

<script>
import { computed } from 'vue'
import MediaIcon from './MediaIcon.vue'
import { mediaTypeLabel } from '../../utils/requestUtils'

export default {
  name: 'TypeBadge',
  components: { MediaIcon },
  props: { type: { type: String, default: 'other' } },
  setup(props) {
    return { label: computed(() => mediaTypeLabel(props.type)) }
  },
}
</script>
