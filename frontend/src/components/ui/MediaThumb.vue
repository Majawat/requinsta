<template>
  <div
    class="flex-none grid place-items-center overflow-hidden bg-slate-800"
    :class="radiusClass"
    :style="{ width: w + 'px', height: h + 'px' }"
  >
    <img
      v-if="cover && !failed"
      :src="cover"
      :alt="alt"
      class="w-full h-full object-cover"
      @error="failed = true"
    />
    <MediaIcon v-else :type="type" :size="iconSize" color="#475569" />
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import MediaIcon from './MediaIcon.vue'

// Cover thumbnail with a faint type-icon placeholder when there is no art.
// Covers are recognition thumbnails only — never the focus.
export default {
  name: 'MediaThumb',
  components: { MediaIcon },
  props: {
    cover: { type: String, default: '' },
    type: { type: String, default: 'other' },
    alt: { type: String, default: '' },
    w: { type: [Number, String], default: 44 },
    h: { type: [Number, String], default: 62 },
    radius: { type: String, default: 'sm' }, // sm = rows (4px), md = detail (6px)
  },
  setup(props) {
    const failed = ref(false)
    const iconSize = computed(() => Math.round(Math.min(Number(props.w), Number(props.h)) * 0.4))
    const radiusClass = computed(() => (props.radius === 'md' ? 'rounded-md' : 'rounded'))
    return { failed, iconSize, radiusClass }
  },
}
</script>
