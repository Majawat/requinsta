<template>
  <div class="flex flex-col items-center gap-3 text-center px-4 py-8">
    <div v-if="$slots.icon || icon" class="grid place-items-center w-11 h-11 rounded-xl bg-slate-800">
      <slot name="icon">
        <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="#475569" stroke-width="2" stroke-linecap="round">
          <circle cx="11" cy="11" r="7" /><line x1="16.5" y1="16.5" x2="21" y2="21" />
        </svg>
      </slot>
    </div>
    <div class="text-base font-semibold text-slate-200">{{ title }}</div>
    <p v-if="body" class="text-[13px] leading-relaxed text-slate-400 max-w-[260px] text-pretty">{{ body }}</p>
    <button v-if="actionLabel" @click="$emit('action')" class="mt-1" :class="actionPrimary ? 'btn-primary' : 'btn-secondary'">
      {{ actionLabel }}
    </button>
  </div>
</template>

<script>
// Every empty state names the situation in the user's words and offers exactly
// one next action.
export default {
  name: 'EmptyState',
  props: {
    title: { type: String, required: true },
    body: { type: String, default: '' },
    actionLabel: { type: String, default: '' },
    actionPrimary: { type: Boolean, default: true },
    icon: { type: Boolean, default: true },
  },
  emits: ['action'],
}
</script>
