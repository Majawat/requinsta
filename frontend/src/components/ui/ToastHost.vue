<template>
  <div class="fixed inset-x-0 bottom-0 z-[60] flex flex-col items-center gap-2 px-4 pb-24 lg:pb-6 pointer-events-none">
    <transition-group name="toast" tag="div" class="w-full max-w-sm flex flex-col gap-2">
      <div
        v-for="t in ui.toasts"
        :key="t.id"
        class="pointer-events-auto flex items-center gap-2.5 rounded-[10px] bg-slate-900 px-3.5 py-3 shadow-toast border"
        :class="t.type === 'error' ? 'border-rose-400/30' : 'border-emerald-400/30'"
      >
        <svg
          v-if="t.type === 'error'"
          width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#fb7185"
          stroke-width="2.2" stroke-linecap="round" class="flex-none"
        >
          <circle cx="12" cy="12" r="9" /><line x1="12" y1="8" x2="12" y2="13" /><line x1="12" y1="16" x2="12" y2="16" />
        </svg>
        <svg
          v-else
          width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#34d399"
          stroke-width="2.4" stroke-linecap="round" class="flex-none"
        >
          <polyline points="4 12.5 9.5 18 20 6" />
        </svg>
        <div class="flex-1 text-[13px] font-medium text-slate-200" v-html="t.message"></div>
        <button
          v-if="t.actionLabel"
          @click="ui.runToastAction(t)"
          class="text-xs font-semibold text-indigo-300 hover:text-indigo-200"
        >
          {{ t.actionLabel }}
        </button>
      </div>
    </transition-group>
  </div>
</template>

<script>
import { useUiStore } from '../../stores/ui'

export default {
  name: 'ToastHost',
  setup() {
    return { ui: useUiStore() }
  },
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
