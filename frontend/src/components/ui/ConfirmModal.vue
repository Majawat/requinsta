<template>
  <teleport to="body">
    <transition name="confirm-fade">
      <div v-if="open" class="fixed inset-0 z-[70] flex items-end lg:items-center justify-center p-0 lg:p-4" @keydown.esc="$emit('cancel')">
        <div class="absolute inset-0 bg-slate-950/70 backdrop-blur-[2px]" @click="$emit('cancel')"></div>
        <div class="relative w-full lg:max-w-sm bg-slate-900 border-t lg:border border-slate-700 rounded-t-2xl lg:rounded-2xl p-5 shadow-sheet">
          <h2 class="text-base font-bold text-slate-100">{{ title }}</h2>
          <p v-if="message" class="text-sm text-slate-400 mt-1.5 text-pretty">{{ message }}</p>
          <div class="flex justify-end gap-2 mt-5">
            <button class="btn-ghost btn-sm" @click="$emit('cancel')">{{ cancelLabel }}</button>
            <button :class="danger ? 'btn-deny' : 'btn-primary'" class="btn-sm" :disabled="busy" @click="$emit('confirm')">
              {{ busy ? '…' : confirmLabel }}
            </button>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script>
// Reusable confirmation for destructive actions (cancel/delete a request, etc.).
export default {
  name: 'ConfirmModal',
  props: {
    open: { type: Boolean, default: false },
    title: { type: String, required: true },
    message: { type: String, default: '' },
    confirmLabel: { type: String, default: 'Confirm' },
    cancelLabel: { type: String, default: 'Cancel' },
    danger: { type: Boolean, default: true },
    busy: { type: Boolean, default: false },
  },
  emits: ['confirm', 'cancel'],
}
</script>

<style scoped>
.confirm-fade-enter-active,
.confirm-fade-leave-active { transition: opacity 0.15s ease; }
.confirm-fade-enter-from,
.confirm-fade-leave-to { opacity: 0; }
</style>
